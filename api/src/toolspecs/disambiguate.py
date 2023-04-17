from pydantic import BaseModel
from ..langmodel_file import TOKENISER_DISAMB_GT_DESC_PMHFST
from ..langmodel_file import DISAMBIGUATOR_CG3

summary = "disambiguate"
description = """
Gives the relevant morphological analysis of each word in context.

`echo "$INPUT" | hfst-tokenize -cg tools/tokenisers/tokeniser-disamb-gt-desc.pmhfst | vislcg3 -g src/cg3/disambiguator.cg`

The output structure is parsed and sent as json.
"""


class WordDisamb(BaseModel):
    root_word: str
    classes: str


class ResponseLine(BaseModel):
    input_word: str
    word_disambs: list[WordDisamb]


def pipeline_stdout_to_json(stdout) -> list[ResponseLine]:
    out = []
    # { input_word, input_word_result },
    # where input_word_result = {
    #   root_word, classes }

    for line in stdout.split("\n"):
        line = line.strip()

        if line == "":
            continue
        elif line.startswith("\"<"):
            input_word = line[2:-2]
            word_disambs = []
        elif line == ":":
            out.append({
                "input_word": input_word,
                "word_disambs": word_disambs
            })
        else:
            q1 = line.index('"') + 1
            q2 = line.index('"', q1)
            root_word = line[q1:q2]
            w_ind = line.index("<")
            classes = line[q2 + 2:w_ind - 1]

            word_disambs.append({
                "root_word": root_word,
                "classes": classes,
            })
    out.append({
        "input_word": input_word,
        "word_disambs": word_disambs,
    })

    return out


pipeline = [
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
    pipeline_stdout_to_json
]
