## Installing

Requires python version >= 3.10 (possibly 3.11?)

rewriting to support older python versions should not
be too difficult, if necessary

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
