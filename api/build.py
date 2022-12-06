import asyncio
import argparse
import inspect
import subprocess
import sys
from itertools import count
from functools import partial
from multiprocessing import cpu_count
from os import get_terminal_size

builtin_print = __builtins__.print

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


DOCKERFILE_lang = """
FROM fst-compiler
ENV GIELLA_LIBS=/progs
WORKDIR /progs
RUN git clone --depth 1 https://github.com/giellalt/lang-{lang}
WORKDIR /progs/lang-{lang}
RUN git log -n 1 --format=format:"%h %cI" > REPO_INFO
RUN autoreconf -i
RUN ./configure --enable-fst-hyphenator --enable-spellers --enable-tokenisers --enable-phonetic --enable-tts
RUN make -j
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


async def _write(fd, data):
    fd.write(data)
    await fd.drain()
    fd.close()

async def _read(fd):
    line = await fd.readline()
    return line


COLUMNS = get_terminal_size().columns

def logit(n, title, s):
    s = s.strip()
    if s.startswith("--->"):
        return
    avail = COLUMNS - len(title)
    if len(s) > avail:
        s = s[:avail - 3] + "..."
    builtin_print(f"\x1b[{n}F\x1b[K", end="")
    builtin_print(f"{title}...{s}", end="")
    builtin_print(f"\x1b[{n}E", end="")
    sys.stdout.flush()


async def worker(q, r, verbose=False):
    while True:
        try:
            idx, f, print_fn = q.get_nowait()
        except asyncio.QueueEmpty:
            break

        f, *args = f

        res = await f(*args, verbose=verbose, print=print_fn)

        r.put_nowait([idx, res])
        q.task_done()


async def docker_build_compiler(verbose, print):
    return await run_docker_build("compiler", DOCKERFILE_compiler, verbose, print)


async def docker_build_lang(lang, lang_files, verbose, print):
    lang_files_needed = " ".join(lang_files[lang])
    input = DOCKERFILE_lang.format(lang=lang, lang_files_needed=lang_files_needed)
    return await run_docker_build(f"lang-{lang}", input, verbose, print)


async def docker_build_app(langs, verbose, print):
    input = DOCKERFILE_app

    COPY_FROM_LANGS = ""
    for lang in langs:
        COPY_FROM_LANGS += DOCKERFILE_APP_COPY_LANG_FILES.format(lang=lang)

    input = input.format(COPY_FROM_LANGS=COPY_FROM_LANGS)

    return await run_docker_build("app", input, verbose, print)


async def run_docker_build(imagetag, input, verbose=False, print=print):
    assert isinstance(input, str), "input must be string"
    input = input.strip().encode("utf-8")

    proc = await asyncio.create_subprocess_shell(
            f"docker build -t fst-{imagetag} -",
            limit=4096,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    # prevent deadlock
    # see https://stackoverflow.com/questions/57730010/python-asyncio-subprocess-write-stdin-and-read-stdout-stderr-continuously
    _, line1 = await asyncio.gather(
        _write(proc.stdin, input),
        _read(proc.stdout)
    )

    lookfor = bytes(f"Successfully tagged fst-{imagetag}", encoding="utf-8")

    if line1.startswith(lookfor):
        print("done")
        return True

    print(line1.decode("utf-8"))

    imagetag_bytes = imagetag.encode("utf-8")
    while True:
        line = await proc.stdout.readline()
        if line.startswith(lookfor):
            print("done")
            return imagetag
        elif line == b"":
            print("Error: unexpected EOF")
            return False
        else:
            print(line.decode("utf-8").strip())


async def run_assignments(*assignments, verbose=False):
    n = len(assignments)
    names, funcs = zip(*assignments)

    if verbose:
        print_fns = [ print for _ in range(n) ]
    else:
        print_fns = [ partial(logit, i, name) for i, name in zip(range(n, 0, -1), names) ]

    q = asyncio.Queue()
    for idx, fn, print_fn in zip(count(), funcs, print_fns):
        q.put_nowait([idx, fn, print_fn])

    for name in names:
        print(name + "...(waiting)")

    r = asyncio.Queue()
    cancelled = asyncio.Event()
    tasks = [asyncio.create_task(worker(q, r, verbose)) for _ in range(cpu_count())]

    gathered = None

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError as e:
        print("cancelled")

    results = [None for _ in range(n)]
    while True:
        try:
            res = r.get_nowait()
        except asyncio.QueueEmpty:
            break

        idx, result = res
        results[idx] = result

    return results if len(results) > 1 else results[0]


def normalize_pipelines(pipelines):
    if isinstance(pipelines, list):
        return {"*": pipelines}
    else:
        return pipelines

async def read_pipeline_specs():
    """Read all pipeline specs (from src/pipelines), to populate
    which files all languages need. Some languages need more files
    than others.

    Ideally, this information can also be used to compile only the
    output artifacts that is needed...but it might be quick enough
    to just compile "everything" and pick what we need."""
    needed = { lang: set() for lang in LANGS }

    from src import toolspecs
    from src.util import PartialPath

    for toolname, spec in inspect.getmembers(toolspecs):
        if toolname.startswith("__"):
            continue
        pipelines = normalize_pipelines(spec.pipeline)
        for lang, pipeline in pipelines.items():
            for program in pipeline:
                if not isinstance(program, list):
                    continue
                for item in program:
                    if not isinstance(item, PartialPath):
                        continue
                    needed_path = item.p

                    if lang == "*":
                        # add to all langs
                        for currentlang in needed:
                            needed[currentlang].add(needed_path)
                    else:
                        needed[lang].add(needed_path)

    return needed


async def main(langs, no_app=False, verbose=False):
    have_compiler = await run_assignments(
        ("Make image: compiler", [docker_build_compiler]),
        verbose=verbose
    )
    if not have_compiler:
        msg = "Error creating compiler"
        if not verbose:
            msg += ", run again with -v for verbose output"
        print(f"{sys.argv[0]} failed: {msg}")
        return

    print("Reading lang specs to determine which output files is needed...", end="")
    lang_files = await read_pipeline_specs()
    print("done")
    lang_assignments = []
    for lang in langs:
        lang_assignments.append(
            (f"Make image: lang-{lang}", [docker_build_lang, lang, lang_files])
        )
    have_langs = await run_assignments(*lang_assignments, verbose=verbose)
    if not isinstance(have_langs, list):
        have_langs = [have_langs]

    if no_app:
        print("Skipping last step (Make image: app) due to --no-app")
        return

    if not all(have_langs):
        print("Cannot continue due to missing languages")
        return

    have_langs = [ lang[5:] for lang in have_langs ]

    app_assignment = ("Make image: app", [docker_build_app, have_langs])
    have_app = await run_assignments(app_assignment, verbose=verbose)
    if not have_app:
        msg = "Error creating app"
        if not verbose:
            msg += ", run again with -v for verbose output"
        print(msg)
    else:
        print("done")


def parse_args():
    langs_help = "language codes of language models to build, in 3-letter iso-639-3 format. use --langs to just print out a list of supported languages"
    showlangs_help = "don't run normal build, just show a list of supported languages"
    verbose_help = "prints all messages (not filtered) on new lines, instead of filtering some lines and overwriting previous lines"
    no_app_help="stop after making langauge models, do not run the final step where the app image is made"
    prog_description = "uses docker to create images of compiled language models, and finally makes a deployable image of the app with all the compiled language artifacts from all languages that it needs to be able to run all defined pipelines"


    parser = argparse.ArgumentParser(prog="build", description=prog_description)
    parser.add_argument("langs", nargs="*", help=langs_help)
    parser.add_argument("--langs", dest="showlangs", action="store_true", help=showlangs_help)
    parser.add_argument("--verbose", "-v", action="store_true", help=verbose_help)
    parser.add_argument("--no-app", "-n", action="store_true", help=no_app_help)

    args = parser.parse_args()

    if args.showlangs:
        print(" ".join(LANGS))
        sys.exit()

    if len(args.langs) == 0:
        args.langs = LANGS
    else:
        for lang in args.langs:
            if lang not in LANGS:
                parser.print_help()
                return None
            
    return args


if __name__ == "__main__":
    args = parse_args()

    if args is not None:
        asyncio.run(main(args.langs, no_app=args.no_app, verbose=args.verbose))
