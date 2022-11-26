from sys import exit
from os import environ
from pathlib import Path
from collections import defaultdict
import logging

try:
    GTLANGS = Path(environ.get("GTLANGS"))
except TypeError:
    logging.warning("Environment variable GTLANGS not found, running without any fst functionality")
    GTLANGS = None

