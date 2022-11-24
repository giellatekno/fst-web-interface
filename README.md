# fst-web-interface

The front-end web interface with accompanying API for the collection of language tools.
A Svelte (pure svelte, not _sveltekit_) web app, which builds into an html/css/js bundle,
hosted statically, that queries a Python-based API for it's dynamic content.


## Development

### Prerequisites

Being a web project, make sure to have a working version of `node`, as
well as `npm` (or `pnpm`) installed on your system.

Packages called `node` or `nodejs` should be available in most
distributions. `nvm` ("node version manager") is an alternative great
way to be able to have mulitple versions of node installed on a system,
and quickly switch between them.

For FastAPI, minimum required python version is 3.10. `pyenv` (python version
manager) will let you install mulitple python versions on your system, and
switch between them. It's basically for Python what nvm is for Node.


### Installation

To run the development server, navigate to the folder after cloning,
and install the dependencies.

```bash
git clone https://github.com/giellatekno/fst-web-interface
cd fst-web-interface
npm install
npm run dev
```

Now visit the locally running development server at [localhost:5173](http://localhost:5173).
Modifications to source files will instantly be reflected in the browser window, due to
something called "hot module reloading".

To run the api in development, navigate to the folder, create a virtual environment,
install requirements, and then run the web server:

```bash
cd fst-web-interface/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

Now the API is accessible at port 8000, and two different OpenAPI schema explorers are
available at [/redoc](http://localhost:8000/redoc) and [/docs](http://localhost:8000/docs).
In my opinon, the /redoc one is nicer, but the /docs one will let you test queries to the
API directly on the documentation site.


### Development after initial setup

For the front-end app, `npm install` is only required when first setting up the
development. Likewise, for python, the steps to install the virtual environment
(`python -m venv .venv`) and installing required packages (`pip install -r requirements.txt`)
are first-time-only required steps.


## Resources

The javascript frontend framework in this project is Svelte.
Read about it at [svelte.dev](https://svelte.dev/).

The API framework is FastAPI. Read about it at [fastapi.tiangolo.com](https://fastapi.tiangolo.com/).


## Deployment

At this point, how we do deployment for this project is yet to be
determined.

The Svelte app builds to static html/css/js, and can be served by any
web server. But keep in mind that it is a SPA, and as such, all requests
for "children" routes should all resolve to index.html.

For the API, there are numerous options, including containerized type
setups, documented on the FastAPI website.

