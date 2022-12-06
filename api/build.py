import asyncio
import argparse
import subprocess
import sys
from itertools import count
from functools import partial
from multiprocessing import cpu_count
from os import get_terminal_size

builtin_print = __builtins__.print

# lang: est  not in github

# After initial "build all", these langs seems to be ok:
#  ciw cor evn fit fkv gle hdn
#  ipk izh kca kpv liv mns
#  myv nio nob olo rmf sjd
#  sje sma som vep vot yrk

LANGS = [
    "bxr", "ciw", "cor", "evn",
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
RUN tar -czf lang-{lang}.tar.gz \
        REPO_INFO \
        tools/tokenisers/tokeniser-disamb-gt-desc.pmhfst \
        tools/hyphenators/hyphenator-gt-desc.hfstol \
        src/analyser-gt-desc.hfstol \
        src/generator-gt-norm.hfstol \
        src/cg3/disambiguator.cg3 \
        src/cg3/dependency.cg3 \
        src/transcriptions/transcriptor-numbers-digit2text.filtered.lookup.hfstol \
        src/phonetics/txt2ipa.compose.hfst
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
    avail = COLUMNS - len(title)
    s = s.strip()
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


async def docker_build_lang(lang, verbose, print):
    input = DOCKERFILE_lang.format(lang=lang)
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


async def main(langs, verbose=False):
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

    lang_assignments = []
    for lang in langs:
        lang_assignments.append(
            (f"Make image: lang-{lang}", [docker_build_lang, lang])
        )
    have_langs = await run_assignments(*lang_assignments, verbose=verbose)
    if not isinstance(have_langs, list):
        have_langs = [have_langs]
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
    parser = argparse.ArgumentParser(prog="build")
    parser.add_argument("langs", nargs="*")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

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
        asyncio.run(main(args.langs, verbose=args.verbose))
