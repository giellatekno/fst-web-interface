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
