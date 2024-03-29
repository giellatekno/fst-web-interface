from pydantic import BaseModel
import re
from ..langmodel_file import TOKENISER_DISAMB_GT_DESC_PMHFST
from ..langmodel_file import DEPENDENCY_CG3
from ..langmodel_file import DISAMBIGUATOR_CG3
from ..langmodel_file import KORP_CG3

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
            if item_match:
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
        TOKENISER_DISAMB_GT_DESC_PMHFST,
    ],
    [
        "vislcg3",
        "-g",
        DISAMBIGUATOR_CG3,
    ],
    [
        "vislcg3",
        "-g",
        KORP_CG3,
    ],
    [
        "vislcg3",
        "-g",
        DEPENDENCY_CG3,
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
            TOKENISER_DISAMB_GT_DESC_PMHFST,
        ],
        [
            "vislcg3",
            "-g",
            DISAMBIGUATOR_CG3,
        ],
        [
            "vislcg3",
            "-g",
            DEPENDENCY_CG3,
        ],
        pipeline_stdout_to_json
    ]
}
