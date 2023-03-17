"""
A script that runs various Dockerfiles. The dockerfiles are kept as inline
strings in this file. They are:

    fst-compiler - hfst nightly compiler
    fst-lang-xxx - compiled language xxx (giellalt/lang-xxx)
    fst-app - gunicorn running the fastapi application

So, the compiler is first built. Then, using the comiler, all specified
languages are built in parallel, after which the app is finally built (which
of course requires the language models).

The final fst-app should be directly depoyable in any container hosting
provider.
"""
import asyncio
import argparse
import inspect
import pathlib
import sys

from docker_wrapper import run_docker_build
from docker_wrapper import run_assignments


LANGS = [
    "ciw", "cor", "evn",
    "fao", "fin", "fit", "fkv", "gle",
    "hdn", "ipk", "izh", "kal", "kca",
    "koi", "kpv", "liv", "mdf", "mhr",
    "mns", "mrj", "myv", "nio", "nob",
    "olo", "rmf", "rus", "sjd", "sje",
    "sma", "sme", "smj", "smn", "sms",
    "som", "udm", "vep", "vot", "vro",
    "yrk",
]


DOCKERFILE_compiler = """
FROM ubuntu:20.04
RUN apt-get update
#RUN apt-get install locales
#RUN locale-gen en_US.UTF-8
#RUN update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
#ENV LANG=en_US
#ENV LC_ALL=en_US.UTF-8
ENV DEBIAN_FRONTEND="noninteractive" TZ="Europe/Oslo"

#RUN apt-get -y install curl bc
# dont have: cmake libtool wget antiword wv python3-pip (and all other pythons I assume)

RUN apt-get -y install bc curl git autoconf automake cmake libtool wget antiword wv python3-pip python3-bs4 python3-lxml python3-html5lib python3-feedparser python3-yaml python3-tidylib

RUN curl https://apertium.projectjj.com/apt/install-nightly.sh | bash
RUN apt-get -yf install apertium-all-dev cg3 hfst

RUN mkdir -p /progs

# giella-core
WORKDIR /progs
RUN git clone --depth 1 https://github.com/giellalt/giella-core
WORKDIR /progs/giella-core
RUN ./autogen.sh
RUN ./configure
RUN make -j

# shared-mul
WORKDIR /progs
RUN git clone --depth 1 https://github.com/giellalt/shared-mul
WORKDIR /progs/shared-mul
## what do I need to do here?

# shared-smi
WORKDIR /progs
RUN git clone --depth 1 https://github.com/giellalt/shared-smi
WORKDIR /progs/shared-smi
RUN autoreconf -i
RUN ./configure
"""


DOCKERFILE_clone_lang = """
FROM fst-compiler
ENV GIELLA_LIBS=/progs
WORKDIR /progs
RUN git clone --depth 1 https://github.com/giellalt/lang-{lang}
WORKDIR /progs/lang-{lang}
RUN git log -n 1 --format=format:"%h %cI" > REPO_INFO
"""

DOCKERFILE_make_lang = """
FROM fst-lang-source-{lang}
#ENV LANG="en_US.UTF-8" LC_ALL="en_US.UTF-8"
WORKDIR /progs/lang-{lang}
#RUN autoreconf -i
RUN ./autogen.sh
RUN ./configure --enable-fst-hyphenator --enable-spellers --enable-tokenisers --enable-phonetic --enable-tts
RUN make -j
# does it fail to build because parallel?
#RUN make
#RUN tar -czf lang-{lang}.tar.gz \
#        REPO_INFO \
#        tools/tokenisers/tokeniser-disamb-gt-desc.pmhfst \
#        tools/hyphenators/hyphenator-gt-desc.hfstol \
#        src/analyser-gt-desc.hfstol \
#        src/generator-gt-norm.hfstol \
#        src/cg3/disambiguator.cg3 \
#        src/cg3/dependency.cg3 \
#        src/transcriptions/transcriptor-numbers-digit2text.filtered.lookup.hfstol \
#        src/phonetics/txt2ipa.compose.hfst
RUN tar -czf lang-{lang}.tar.gz {lang_files_needed}
"""

DOCKERFILE_app = """
FROM python:3.11
RUN apt-get update
ENV DEBIAN_FRONTEND="noninteractive" TZ="Europe/Oslo"
RUN apt-get -y install curl
RUN curl https://apertium.projectjj.com/apt/install-nightly.sh | bash

# note: only cg3 and hfst, not "all-dev" (for smaller image size)
RUN apt-get -yf install cg3 hfst

{COPY_FROM_LANGS}

RUN mkdir /app
WORKDIR /app
RUN git clone --depth 1 https://github.com/giellatekno/fst-web-interface
WORKDIR /app/fst-web-interface/api
RUN pip install -r requirements.deploy.txt

ENV WEB_CONCURRENCY=4
ENV GTLANGS=/progs

EXPOSE 8000
CMD ["gunicorn", "src.main:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
"""


DOCKERFILE_APP_COPY_LANG_FILES = """
COPY --from=fst-lang-{lang} /progs/lang-{lang}/lang-{lang}.tar.gz /progs/lang-{lang}/lang-{lang}.tar.gz
WORKDIR /progs/lang-{lang}
RUN tar -xzf lang-{lang}.tar.gz && rm lang-{lang}.tar.gz
"""


async def docker_build_compiler(verbose, print):
    return await run_docker_build(
        "fst-compiler", DOCKERFILE_compiler, verbose, print)


async def docker_build_clone_lang(lang, verbose, print):
    return await run_docker_build(
        f"fst-lang-source-{lang}",
        input=DOCKERFILE_clone_lang.format(lang=lang),
        verbose=verbose, print=print)


async def docker_build_make_lang(lang, lang_files, verbose, print):
    return await run_docker_build(
        f"fst-lang-{lang}",
        input=DOCKERFILE_make_lang.format(
            lang=lang, lang_files_needed=" ".join(lang_files[lang])
        ),
        verbose=verbose,
        print=print
    )


async def docker_build_app(langs, verbose, print):
    input = DOCKERFILE_app

    COPY_FROM_LANGS = ""
    for lang in langs:
        COPY_FROM_LANGS += DOCKERFILE_APP_COPY_LANG_FILES.format(lang=lang)

    input = input.format(COPY_FROM_LANGS=COPY_FROM_LANGS)
    print(input)

    return await run_docker_build("fst-app", input, verbose, print)


# def normalize_pipelines(pipelines):
#     if isinstance(pipelines, list):
#         return {"*": pipelines}
#     else:
#         return pipelines
#
#
# async def read_pipeline_specs():
#     """Read all pipeline specs (from src/pipelines), to populate
#     which files all languages need. Some languages need more files
#     than others.
#
#     Ideally, this information can also be used to compile only the
#     output artifacts that is needed...but it might be quick enough
#     to just compile "everything" and pick what we need."""
#     needed = {lang: set() for lang in LANGS}
#
#     from src import toolspecs
#     from src.util import PartialPath
#
#     for toolname, spec in inspect.getmembers(toolspecs):
#         if toolname.startswith("__"):
#             continue
#         pipelines = normalize_pipelines(spec.pipeline)
#         for lang, pipeline in pipelines.items():
#             for program in pipeline:
#                 if not isinstance(program, list):
#                     continue
#                 for item in program:
#                     if not isinstance(item, PartialPath):
#                         continue
#                     needed_path = item.p
#
#                     if lang == "*":
#                         # add to all langs
#                         for currentlang in needed:
#                             needed[currentlang].add(needed_path)
#                     else:
#                         needed[lang].add(needed_path)
#
#     return needed


async def do_extract_tarball(lang, verbose=False, print=print):
    print("copying")
    cmd = (f"docker cp $(docker create --name tc-{lang} fst-lang-{lang}):"
           f"/progs/lang-{lang}/lang-{lang}.tar.gz ./compiled/lang-{lang}.tar.gz"
           f" && docker rm tc-{lang}")
    proc = await asyncio.create_subprocess_shell(cmd)
    await proc.wait()
    print("done")


async def run_extract_tarballs(langs, verbose=False, print=print):
    """Extract tarballs from images by running the image and catting out the files."""
    # first, make sure you are in the correct folder
    folder = pathlib.Path(".") / "compiled"
    folder.mkdir(exist_ok=True)
    assignments = [
        (f"Extract tarball: lang-{lang}.tar.gz", [do_extract_tarball, lang])
        for lang in langs
    ]
    await run_assignments(*assignments)


async def main(args):
    if args.print_langs:
        # --print-langs
        print(" ".join(LANGS))
        return 0

    langs, lang_files, verbose = args.langs, args.lang_files, args.verbose
    no_app, extract_tarballs = args.no_app, args.extract_tarballs

    assignments = ("Make image: fst-compiler", [docker_build_compiler])
    if not await run_assignments(assignments, verbose=verbose):
        print(f"{sys.argv[0]} failed: Error when building fst-compiler")
        return 1

    assignments = [
        (
            f"Make image: fst-lang-source-{lang}",
            [docker_build_clone_lang, lang]
        )
        for lang in langs
    ]
    if not await run_assignments(*assignments, verbose=verbose):
        print(f"{sys.argv[0]} failed: Error when building cloner images")
        return 1

    lang_assignments = [
        (
            f"Make image: fst-lang-{lang}",
            [docker_build_make_lang, lang, lang_files]
        )
        for lang in langs
    ]
    have_langs = await run_assignments(*lang_assignments, verbose=verbose)
    if not isinstance(have_langs, list):
        have_langs = [have_langs]

    have_langs = [lang[9:] for lang in have_langs if isinstance(lang, str)]
    print(f"{have_langs=}")

    if not have_langs:
        print("Error: Cannot continue, no languages compiled successfully.")
        return 1

    if extract_tarballs:
        await run_extract_tarballs(have_langs)

    if no_app:
        print("Skipping last step (Make image: app) due to --no-app")
        return

    if not all(have_langs):
        print("Cannot continue due to missing languages")
        return 1

    app_assignment = ("Make image: app", [docker_build_app, have_langs])
    have_app = await run_assignments(app_assignment, verbose=verbose)
    if not have_app:
        msg = "Error creating app"
        if not verbose:
            msg += ", run again with -v for verbose output"
        print(msg)
        return 1
    else:
        print("done")


def parse_args():
    parser = argparse.ArgumentParser(prog="build", description=__doc__)
    parser.add_argument(
        "langs",
        nargs="*",
        choices=LANGS + ["ALL"],
        help=(
            "Language codes of language models to build, in 3-letter "
            "iso-639-3 format. use --print-langs to just print out a list "
            "of supported languages"
        ),
    )
    parser.add_argument(
        "--lang-files",
        required=True,
        type=argparse.FileType("r"),
        help=(
            "Required. Path to json file describing which gt files are "
            "needed for which language. Use toolspec.py to rebuild it."
        ),
    )
    parser.add_argument(
        "--print-langs",
        action="store_true",
        help=(
            "Don't run normal build, just show a list of all "
            "supported languages"
        ),
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help=(
            "prints all messages (not filtered) on new lines, instead of "
            "filtering some lines and overwriting previous lines"
        ),
    )
    parser.add_argument(
        "--no-app",
        "-n",
        action="store_true",
        help=(
            "stop after making langauge models, do not run the final "
            "step where the app image is made"
        ),
    )
    parser.add_argument(
        "--extract-tarballs",
        action="store_true",
        help=(
            "After making the languages, extract the tarball of compiled "
            "artifacts to the host system (will be stored in folder compiled/)"
        ),
    )

    args = parser.parse_args()

    import json
    args.lang_files = json.load(args.lang_files)

    if "ALL" in args.langs:
        args.langs = LANGS

    return args


if __name__ == "__main__":
    args = parse_args()

    ret = asyncio.run(main(args))
    if isinstance(ret, int) and ret > 0 and not args.verbose:
        print("run again with -v for verbose output")

    raise SystemExit(ret)
