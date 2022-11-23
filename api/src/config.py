from sys import exit
from os import environ
from pathlib import Path
from collections import defaultdict

try:
    GTLANGS = Path(environ.get("GTLANGS"))
except TypeError:
    print("Environment variable GTLANGS not found, aborting")
    exit(1)

