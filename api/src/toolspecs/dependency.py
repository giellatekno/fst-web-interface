from pydantic import BaseModel
from ..util import PartialPath
import re

summary = "dependency"
description = """
Gives the relevant morphological analysis of each word in context, as
well as syntactic functions and dependency structure

`echo "$INPUT" | hfst-tokenize -cg tools/tokenisers/tokeniser-disamb-gt-desc.pmhfst | vislcg3 -g src/cg3/disambiguator.cg3 | vislcg3 -g lang-$LANG/cg3/korp.cg3 | vislcg3 -g lang-$LANG/cg3/dependency.cg3`

The output structure is parsed and sent as json.
"""
line_re = r'"\<(?P<word>\w+)\>"'


class Def(BaseModel):
    root: str
    wcs: str
    dep: str


class ResponseLine(BaseModel):
    word: str
    defs: list[Def]


# TODO dot handling.
# dots at the end of a "sentence" we can just easily remove,
# but if a word has a dot in it, for example: "f.eks.", or
# "Prof.", we don't currently handle it


WORD = re.compile(r'''
"<(?P<word>(\w+|,))>"              # capture the input word, can be ","
    (?P<lines>
        (
            \s+(.+)\n
        )+
    )
''', re.MULTILINE | re.VERBOSE)

ITEM = re.compile(r'''
     "(?P<root>(\w+|,))"               # root word is in quotes, can be ","
     \ (?P<wcs>(\?|\w+(\ \w+)*))       # wcs = word classes
     \ \#(?P<dep>\d+->\d+)             # finally capture the dependency "X->X"
''', re.MULTILINE | re.VERBOSE)


def pipeline_stdout_to_json(output) -> list[ResponseLine]:
    # if ends with ".", remove it
    if output.endswith("."):
        output = output[:-1]

    out = []

    for m in WORD.finditer(output):
        word = m["word"]
        lines = m["lines"].strip()

        defs = []
        for line in lines.split("\n"):
            line = line.strip()
            item_match = ITEM.match(line)
            defs.append(item_match.groupdict())

        out.append({
            "word": word,
            "defs": defs
        })

    return out


# TODO!! some languages have a different pipeline!
with_korp = [
    [
        "hfst-tokenize",
        "-cg",

        # built with: ./configure --enable-tokenisers
        PartialPath(
            "tools/tokenisers/tokeniser-disamb-gt-desc.pmhfst"
        ),
    ],
    [
        "vislcg3",
        "-g",
        PartialPath(
            "src/cg3/disambiguator.cg3"
        ),
    ],
    [
        "vislcg3",
        "-g",
        PartialPath(
            "src/cg3/korp.cg3"
        ),
    ],
    [
        "vislcg3",
        "-g",
        PartialPath(
            "src/cg3/dependency.cg3"
        ),
    ],
    pipeline_stdout_to_json
]


pipeline = {
    # these languages have an additional step in the pipeline
    "fao": with_korp,
    "sma": with_korp,
    "sme": with_korp,
    "smj": with_korp,
    # "nob": with_korp,

    # for all other languages, this is the pipeline
    "*": [
        [
            "hfst-tokenize",
            # note: -L for nicer output (doesn't separate by ":", and does
            # not do anything with the commas, but we might want to)
            "-cgL",

            # built with: ./configure --enable-tokenisers
            PartialPath(
                "tools/tokenisers/tokeniser-disamb-gt-desc.pmhfst"
            ),
        ],
        [
            "vislcg3",
            "-g",
            PartialPath(
                "src/cg3/disambiguator.cg3"
            ),
        ],
        [
            "vislcg3",
            "-g",
            PartialPath(
                "src/cg3/dependency.cg3"
            ),
        ],
        pipeline_stdout_to_json
    ]
}
