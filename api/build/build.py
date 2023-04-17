"""
A script that runs various Dockerfiles. The dockerfiles are kept as inline
strings in this file. They are:

    fst-compiler - hfst nightly compiler
    fst-lang-soruce-xxx - git cloned language sources of language xxx
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
import pathlib
import sys
import json
import datetime

from textwrap import dedent
from pathlib import Path
from functools import partial
from collections import defaultdict

from build.docker_wrapper import docker_build, docker_run, docker_list_images
from build.docker_wrapper import docker_create, docker_rm_container
from build.docker_wrapper import docker_cp_from_image
# from .docker_wrapper import docker_image_rm
from build.run_many import Job, run_jobs
from src.langmodel_file import langmodel_files


def noop(*_args, **_kwargs): pass


class Namespace:
    def __str__(self):
        return str(self.__dict__)


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

# all flags:
# --enable-fst-hyphenator --enable-spellers
# --enable-tokenisers --enable-phonetic --enable-tts

# These files are already present in the repository, all we have to do is
# copy them over
IN_REPO_FILES = {
    # these two are in shared-smi for sami languages!
    "dependency.cg3",
    "korp.cg3",

    "disambiguator.cg3",
}

COMPILE_FLAGS = {
    # tools/tokenisers/<file>
    "tokeniser-disamb-gt-desc.pmhfst": set(["enable-tokenisers"]),

    # src/generator-gt-norm.hfstol"
    "generator-gt-norm.hfstol": None,

    "transcriptor-numbers-digit2text.filtered.lookup.hfstol": None,

    # src/analyser-gt-desc.hfstol
    "analyser-gt-desc.hfstol": None,

    "hyphenator-gt-desc.hfstol": set(["enable-fst-hyphenator"]),
    "txt2ipa.compose.hfst": set(["enable-phonetic", "enable-tts"]),

    # src/cg3/korp.cg3
    "korp.cg3": None,
}


DOCKERFILE_apertium_nightly_base = """
FROM debian:sid
RUN apt-get update && apt-get install -y curl
RUN curl https://apertium.projectjj.com/apt/install-nightly.sh | bash
# sid has more stuff than bookworm (11)...
# RUN echo "deb http://apertium.projectjj.com/apt/nightly sid main" > /etc/apt/sources.list.d/apertium.list
"""


DOCKERFILE_compiler = """
FROM apertium-nightly-base
ENV DEBIAN_FRONTEND="noninteractive" TZ="Europe/Oslo"

# dont have: cmake libtool wget antiword wv python3-pip (and all other pythons I assume)

# RUN apt-get -y install bc curl git autoconf automake cmake libtool wget antiword wv python3-pip python3-bs4 python3-lxml python3-html5lib python3-feedparser python3-yaml python3-tidylib
RUN apt-get-update && \
    apt-get -y install bc git autoconf automake cmake libtool \
    wget antiword python3-pip python3-bs4 python3-lxml python3-html5lib \
    python3-feedparser python3-yaml python3-tidylib gawk icu-devtools \
    cg3 hfst
#RUN apt-get install apertium-all-dev

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


def DOCKERFILE_clone_lang(lang):
    return dedent(f"""
        FROM fst-compiler
        ENV GIELLA_LIBS=/progs
        WORKDIR /progs
        RUN git clone --depth 1 https://github.com/giellalt/lang-{lang}
        WORKDIR /progs/lang-{lang}
        RUN git log -n 1 --format=format:"%h %cI" > REPO_INFO
    """).strip()


def DOCKERFILE_make_lang(lang, compile_flags, files_to_copy):
    compile_flags = " ".join(f"--{flag}" for flag in compile_flags)
    files_to_copy = " ".join(files_to_copy)

    return dedent(f"""
        FROM fst-lang-source-{lang}
        #ENV LANG="en_US.UTF-8" LC_ALL="en_US.UTF-8"
        WORKDIR /progs/lang-{lang}
        #RUN ./autogen.sh
        RUN autoreconf -i
        RUN ./configure {compile_flags}
        RUN make
        RUN tar -czf lang-{lang}.tar.gz {files_to_copy}
    """).strip()


def DOCKERFILE_app(state):
    copy_statements = ""

    if not state.args.no_nightly:
        copy_statements += "COPY --from=apertium-nightly-all-sources /usr/share/giella /usr/share/giella\n"

    if not state.args.no_compile:
        copy_statements += "COPY --from=fst-compiled-langmodel-files /progs/lang-* /progs/\n"

    # copy_statements = dedent(f"""
    #     COPY --from=fst-lang-{lang} /progs/lang-{lang}/lang-{lang}.tar.gz /progs/lang-{lang}/lang-{lang}.tar.gz
    #     WORKDIR /progs/lang-{lang}
    #     RUN tar -xzf lang-{lang}.tar.gz && rm lang-{lang}.tar.gz
    # """)

    return dedent(f"""
        FROM python:3.11
        RUN apt-get update
        ENV DEBIAN_FRONTEND="noninteractive" TZ="Europe/Oslo"
        RUN apt-get -y install curl
        RUN curl https://apertium.projectjj.com/apt/install-nightly.sh | bash
        RUN apt-get -yf install cg3 hfst

        {copy_statements}

        RUN mkdir /app
        WORKDIR /app
        COPY --from=default . /app
        #RUN git clone --depth 1 https://github.com/giellatekno/fst-web-interface
        #WORKDIR /app/fst-web-interface/api
        #WORKDIR /app
        RUN pip install -r requirements.deploy.txt

        ENV WEB_CONCURRENCY=4
        ENV GTLANGS=/progs

        EXPOSE 8000
        CMD ["gunicorn", "src.main:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
    """).strip()


async def extract_langmodel_files(state):
    """Extract language model files from the apertium nightly images,
    and the compiled images, and save them as tarballs for the app to use."""
    if not state.args.extract_tarballs:
        return

    # first, make sure you are in the correct folder
    folder = pathlib.Path(".") / "compiled"
    folder.mkdir(exist_ok=True)
    jobs = [
        Job(
            name="extract",
            title=f"Extract tarball: lang-{lang}.tar.gz",
            coro=partial(
                docker_cp_from_image,
                image=f"fst-lang-{lang}",
                source=f"/progs/lang-{lang}/lang-{lang}.tar.gz",
                destination=f"./compiled/lang-{lang}.tar.gz",
            )
        )
        for lang in state.langs
    ]
    return await run_jobs(jobs, cpu_bound=True)


async def make_fst_compiler_image(state):
    if state.args.no_compile:
        print("Note: Skipping compiling due to --no-compile")
        return

    if not state.langs_to_compile:
        # nothing to do!
        print("Notice: skipping step: make fst compiler, due to no langs needs to be compiled")
        return

    results = await run_jobs([
        Job(
            id="compiler",
            title="Make image: fst-compiler",
            coro=partial(
                docker_build,
                dockerfile=DOCKERFILE_compiler,
                tag="fst-compiler",
                disable_cache=state.args.no_docker_cache,
            ),
        )
    ])

    state.have_compiler = results[0].status == "done"


async def make_fst_lang_sources(state):
    if not state.have_compiler:
        return

    results = await run_jobs([
        Job(
            id=lang,
            title=f"Make image: fst-lang-source-{lang}",
            coro=partial(
                docker_build,
                dockerfile=DOCKERFILE_clone_lang(lang),
                tag=f"fst-lang-source-{lang}",
                disable_cache=state.args.no_docker_cache,
            )
        )
        for lang in state.langs_to_compile
    ])

    for job in results:
        if job.status == "done":
            lang = job.id
            state.langs_to_compile[lang]["have_source"] = True


async def make_fst_lang_models(state):
    if not state.have_compiler:
        return

    results = await run_jobs(
        [
            Job(
                id=lang,
                title=f"Make image: fst-lang-{lang}",
                coro=partial(
                    docker_build,
                    dockerfile=DOCKERFILE_make_lang(
                        lang,
                        compile_flags=opts["compile_flags"],
                        files_to_copy=opts["file_list"],
                    ),
                    tag=f"fst-lang-{lang}",
                    disable_cache=state.args.no_docker_cache,
                )
            )
            for lang, opts in state.langs_to_compile.items()
            if opts["have_source"]
        ],
        cpu_bound=True
    )

    for job in results:
        if job.status == "done":
            lang = job.id
            state.compiled_langs.add(lang)
        else:
            print(job.exception)


async def make_fst_app_image(state):
    if state.args.no_app:
        print("Skipping last step 'Make image: app' due to --no-app")
        return

    if state.failed_langs:
        print("Notice: Some languages did not get built, "
              "continuing build with the successful ones.")
        print("Succeeded with languages:", ", ".join(state.succeeded_langs))
        print("Failed languages:", ", ".join(state.failed_langs))

    dockerfile = DOCKERFILE_app(state)

    results = await run_jobs([
        Job(
            id="fst-app",
            title="Make image: fst-app",
            coro=partial(
                docker_build,
                dockerfile=dockerfile,
                tag="fst-app",
                disable_cache=state.args.no_docker_cache,
                build_context=True,
            )
        )
    ])

    job = results[0]

    if job.exception is not None:
        sio = job.exception.args[0]
        print(sio.getvalue())

    state.have_app = results[0].status == "done"


async def make_apertium_nightly_base(state):
    results = await run_jobs([
        Job(
            id="apertium-nightly-base",
            title="Make image: apertium-nightly-base",
            coro=partial(
                docker_build,
                dockerfile=DOCKERFILE_apertium_nightly_base,
                tag="apertium-nightly-base",
                disable_cache=state.args.no_docker_cache,
            )
        )],
    )
    state.have_apertium_nightly_base = results[0].status == "done"


async def make_apertium_nightly_langmodels(state):
    if not state.have_apertium_nightly_base:
        return

    if state.args.no_nightly:
        print("Notice: Skipping apertium nightly files due to --no-nightly")
        return

    dockerfile = dedent("""
        FROM apertium-nightly-base
        RUN apt-get update
        WORKDIR /tmp
        RUN set -eux; \
            apt-get download giella-{lang} && \
            dpkg --ignore-depends="cg3,hfst,giella-{lang}-speller" --install `ls` && \
            cd /usr/share/giella/{lang} && \
            find . -type f | sed "s/^.\\///" > CONTENTS.txt && \
            rm /tmp/*;
    """).strip()

    # First we download the packages from nightly repo
    results = await run_jobs(
        [
            Job(
                id=lang,
                title=f"Make image: apertium-nightly-lang-{lang}",
                coro=partial(
                    docker_build,
                    dockerfile=dockerfile.format(lang=lang),
                    tag=f"apertium-nightly-lang-{lang}",
                    disable_cache=state.args.no_docker_cache,
                )
            )
            for lang in state.args.langs.keys()
        ],
        cpu_bound=False,
    )

    # filter away the ones that didn't complete succesfully
    ok_langs = [job.id for job in results if job.status == "done"]

    # Gather all nightly sources in one docker image, for easier transfer
    # later on. (this is probably not necessary, but simplifies the dockerfile
    # for the app later on)
    copy_statements = "\n".join(
        f"COPY --from=apertium-nightly-lang-{lang} /usr/share/giella/{lang} /usr/share/giella/{lang}"
        for lang in ok_langs
    )

    apertium_nightly_sources_dockerfile = dedent(f"""
        FROM debian:11
        {copy_statements}
    """)

    await run_jobs(
        [
            Job(
                id="gather",
                title="Gather all apertium nightly langmodel files into one image",
                coro=partial(
                    docker_build,
                    dockerfile=apertium_nightly_sources_dockerfile,
                    tag="apertium-nightly-all-sources",
                    disable_cache=state.args.no_docker_cache,
                )
            )
        ]
    )

    # and finally read out the contents of the /usr/share/giella/LANG folder
    results = await run_jobs(
        [
            Job(
                id=f"{lang}",
                title=f"Read contents of apertium-nightly-lang-{lang}",
                coro=partial(
                    docker_run,
                    image=f"apertium-nightly-lang-{lang}",
                    cmd=f'find /usr/share/giella/{lang} -type f'
                ),
            )
            for lang in ok_langs
        ],
    )

    for job in results:
        lang = job.id
        stdout = job.result[0]
        apertium_files = [line.strip()[22:] for line in stdout.split()]
        state.args.langs[lang].mark_in_apertium(apertium_files)


async def determine_work(state):
    to_compile = {}
    for lang, needed_files in state.args.lang_files.items():
        if lang not in state.args.langs:
            continue

        nightly_set = state.apertium_nightly_contents[lang]
        needed_set = set(Path(file).name for file in needed_files)

        to_compile[lang] = needed_set - nightly_set - IN_REPO_FILES

    langs_to_compile = {}
    for lang in args.langs:
        langs_to_compile[lang] = to_compile[lang]

    state.langs_to_compile = langs_to_compile


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
        # required=True,
        type=argparse.FileType("r"),
        help=(
            "Required. Path to json file describing which gt files are "
            "needed for which language. Use toolspec.py to rebuild it."
        ),
    )
    parser.add_argument(
        "--no-docker-cache",
        action="store_true",
        help=(
            "Do not use the docker cache. Everything will be built from "
            "scratch"
        )
    )
    parser.add_argument(
        "--refetch-nightly-lists",
        choices=["never", "stale", "always"],
        default="stale",
        help=(
            "Refetch the list over files that the nightly builds have of each "
            "language model. The choices are self-explanatory. 'stale' means "
            "to refetch if the cached lists are more than 2 weeks old."
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
        "--no-nightly",
        action="store_true",
        help=(
            "Do not use any language model files from apertium nightly, "
            "but instead compile everything directly from github repo sources"
        ),
    )
    parser.add_argument(
        "--no-compile",
        action="store_true",
        help=(
            "Do not compile language models, only use apertium sources."
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

    if args.print_langs:
        print(" ".join(LANGS))
        raise SystemExit()

    # args.lang_files = json.load(args.lang_files)

    if "ALL" in args.langs:
        args.langs = LANGS

    return args


async def main(args):
    print("Welcome to the fst-app docker image build script.")
    print(f"langauges: {', '.join(args.langs)}")
    print("Hint: Skip a step prematurely with ctrl-c")
    print("Do ctrl-c two times rapidly to abort the entire script")

    state = Namespace()
    langs = {}
    for lang in args.langs:
        langs[lang] = langmodel_files.copy()

    args.langs = langs
    # args.lang_files
    # strucure of langs...
    # I need:
    #   file list
    #      each file needs:
    #      - do we have it in nightly?
    #      - if not, then how do we get it?
    #        + it can be compiled,
    #          in which case we need the ./configure flag(s) for it
    #        + it can be in the repository directly
    state.args = args
    state.have_apertium_nightly_base = None
    state.nightly_langmodel_files = None
    state.have_compiler = None
    state.langs_to_compile = {}
    state.compiled_langs = set()
    state.failed_langs = set()
    state.aborted_langs = set()

    await make_apertium_nightly_base(state)
    await make_apertium_nightly_langmodels(state)

    for lang, files in args.langs.items():
        if files.needs_build():
            state.langs_to_compile[lang] = {
                "compile_flags": files.determine_configure_flags(),
                "file_list": files.missing_files(),
                "have_source": False,
            }

    await make_fst_compiler_image(state)
    await make_fst_lang_sources(state)
    await make_fst_lang_models(state)

    #await extract_langmodel_files(state)
    await make_fst_app_image(state)


if __name__ == "__main__":
    args = parse_args()

    try:
        ret = asyncio.run(main(args))
    except KeyboardInterrupt:
        raise SystemExit(0)

    if isinstance(ret, int) and ret > 0 and not args.verbose:
        print("run again with -v for verbose output")

    raise SystemExit(ret)
