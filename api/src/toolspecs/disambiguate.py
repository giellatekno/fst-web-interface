from ..util import PartialPath

summary = "disambiguate"
description = """
Gives the relevant morphological analysis of each word in context.

`echo "$INPUT" | hfst-tokenize -cg tools/tokenisers/tokeniser-disamb-gt-desc.pmhfst | vislcg3 -g src/cg3/disambiguator.cg`

The output structure is parsed and sent as json.
"""

def pipeline_stdout_to_json(stdout):
    out = []
    #{ input_word, input_word_result },
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
            classes = line[q2 + 2 : w_ind - 1]

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
    pipeline_stdout_to_json
]
