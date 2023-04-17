from pydantic import BaseModel
from ..langmodel_file import TOKENISER_DISAMB_GT_DESC_PMHFST
from ..langmodel_file import ANALYSER_GT_DESC_HFSTOL

summary = "analyze"
description = """
Short description here.

`echo "$INPUT" | hfst-tokenize -q lang-$LANG/tools/tokenisers/tokeniser-disamb-gt-desc.pmhfst | hfst-lookup -q src/analyser-gt-desc.hfstol`

The output structure is parsed and sent as json.
"""


class ResponseLine(BaseModel):
    word: str
    root: str
    cls: str
    props: str


def pipeline_stdout_to_json(stdout) -> list[ResponseLine]:
    # "bok\tbok+CmpNP/None+N+Fem+Sg+Indef\t0,000000\nbok\tbok+N+Fem+Sg+Indef\t0,000000\n\n\t+?\tinf\n\n"

    # bok  \t  bok+CmpNP/None+N+Fem+Sg+Indef  \t  0,000000
    # bok  \t  bok+N+Fem+Sg+Indef   \t    0,000000
    #
    #     \t  +?   \t    inf
    #
    # EOF
    lines = stdout.split("\n")
    out = []
    for line in lines:
        line = line.strip()
        if line == "" or line.startswith("+?"):
            continue

        splits = line.split("\t")
        if len(splits) == 2:
            continue
            word, res = splits
        elif len(splits) == 3:
            word, res, _weight = splits

        # bok+CmpNP/None+N+Fem+Sg+Indef =>
        #  root = bok
        #  allpluses = CmpNP/None, N, Fem, ...
        root, *allpluses = res.split("+")

        # CmpNP/None .. en slags tag? kan det være flere?
        if allpluses[0] == "CmpNP/None":
            cls = f"({allpluses[0]}) {allpluses[1]}"
            props = "+".join(allpluses[2:])
        else:
            cls = allpluses[0]
            props = "+".join(allpluses[1:])

        out.append(dict(word=word, root=root, cls=cls, props=props))

    return out


pipeline = [
    [
        "hfst-tokenize",
        "-q",
        TOKENISER_DISAMB_GT_DESC_PMHFST,
    ],
    [
        "hfst-lookup",
        "-q",
        ANALYSER_GT_DESC_HFSTOL,
    ],
    pipeline_stdout_to_json
]
