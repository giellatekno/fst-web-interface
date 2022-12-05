## Installing

Requires python version >= 3.11

rewriting to support older python versions should not
be _too_ difficult, if necessary (but probably using dockerized
production environment, so should not be a problem)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running

(after having activate the virtual environment with `source .venv/bin/activate`),
simply run

```bash
uvicorn src.main:app --reload
```

To start a local development server.


## Deploying

Exactly how to do this is a work in progress, but so far...

Running `python build.py [lang1, lang2, ...]` will build a docker image that
contains a language compiler (the image is named "fst-compiler"). It is used
as a base to compile languages. It will then also build images for each specificed
`langN` (or all languages if none are specified). When that is all done,
a final image called "fst-app" will be built, that has the necessary tools required
to run the language models, as well as the application itself. It copies in
language model files from the various `fst-lang-XXX` images.

The `fst-app` image can then be run to start the server. It exposes the api on port 8000.

The app spawns with 4 worker threads by default. Exactly how many worker threads to use
is difficult to know. The following command will run the image, and use as many threads
as there are cpu cores. Again, that may not be the most optimal.

```bash
docker run -p 8000:8000 --env WEB_CONCURRENCY=`cat /proc/cpuinfo | grep "cpu cores" | uniq | cut -d ":" -f2 | sed "s/ //g"` fst-app
```
