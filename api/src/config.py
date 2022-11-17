from sys import exit
from os import environ
from pathlib import Path

GTLANGS = environ.get("GTLANGS")
if GTLANGS is not None and GTLANGS[-1] != "/":
    GTLANGS += "/"

if GTLANGS is None:
    print("no environment variable GTLANGS found, aborting")
    exit(1)


generator_langs = []
hyphenator_langs = []
for p in Path(GTLANGS).glob("lang-*"):
    lang = p.name[5:]

    generator_hfstol = p / "src" / "generator-gt-norm.hfstol"
    hyphenator_hfstol = p / "tools" / "hyphenators" / "hyphenator-gt-desc.hfstol"

    if generator_hfstol.is_file():
        generator_langs.append(lang)
    if hyphenator_hfstol.is_file():
        hyphenator_langs.append(lang)
    

print("Available languages for tool `generate`:", ", ".join(generator_langs))
print("Available languages for tool `hyphenate`:", ", ".join(generator_langs))
