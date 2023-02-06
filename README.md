# fst-web-interface

The front-end web interface with accompanying API for the collection of language tools.
A Svelte (pure svelte, not _sveltekit_) web app, which builds into an html/css/js bundle,
hosted statically, that queries a Python-based API for it's dynamic content.

See the full documentation at [giellatekno.github.io/fst-web-interface/][https://giellatekno.github.io/fst-web-interface/].

## Quickstart

Clone the repo, then install and run the client.

```bash
git clone https://github.com/giellatekno/fst-web-interface
cd fst-web-interface/client
npm install
npm run dev
```

The client uses an api, so open up another terminal and run

```bash
cd fst-web-interface/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

See the site at [localhost:5173][localhost:5173]. The API has two nice OpenAPI
interfaces at [localhost:8000/docs][localhost:8000/docs] and
[localhost:8000/redoc][localhost:8000/redoc]. See the full documentation for
more.
