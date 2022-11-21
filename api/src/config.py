from sys import exit
from os import environ
from pathlib import Path

try:
    GTLANGS = Path(environ.get("GTLANGS"))
except TypeError:
    print("Environment variable GTLANGS not found, aborting")
    exit(1)


generator_langs = []
hyphenate_langs = []
transcriber_langs = []
disamb_langs = []
for p in Path(GTLANGS).glob("lang-*"):
    lang = p.name[5:]

    generator_hfstol = p / "src" / "generator-gt-norm.hfstol"
    hyphenate_hfstol = p / "tools" / "hyphenators" / "hyphenator-gt-desc.hfstol"
    transcribe_hfstol = p / "src" / "phonetics" / "txt2ipa.compose.hfst"
    #disamb_cg3 = p / 

    # required files for disambiguate
    #   lang-xxx/tools/tokenisers/tokeniser-disamb-gt-desc.pmhfst
    # build with: ./configure --enable-tokenisers
    disamb_pmhfst = p / "tools" / "tokenisers" / "tokeniser-disamb-gt-desc.pmhfst"

    #  lang-xxx/src/disambiguator.cg3
    # build with: ??? (always built?)
    disamb_cg3 = p / "src" / "cg3" / "disambiguator.cg3"

    if generator_hfstol.is_file():
        generator_langs.append(lang)
    if hyphenate_hfstol.is_file():
        hyphenate_langs.append(lang)
    if transcribe_hfstol.is_file():
        transcriber_langs.append(lang)
    print(f"{lang=}, {disamb_pmhfst.is_file()}")
    print(f"{lang=}, {disamb_cg3.is_file()}")
    if disamb_pmhfst.is_file() and disamb_cg3.is_file():
        disamb_langs.append(lang)

capabilities = {
    "generate": generator_langs,
    "hyphenate": hyphenate_langs,
    "transcribe": transcriber_langs,
    "disambiguate": disamb_langs,
}

for tool, langs in capabilities.items():
    print(f"Available langauges for tool '{tool}': {', '.join(langs)}")
