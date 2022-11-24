from ..util import PartialPath
import re

summary = "dependency"
description = """
Short description here.

Like running `echo "$INPUT" | hfst-tokenize -cg lang-$LANG/tools/tokenisers/tokeniser-disamb-gt-desc.pmhfst | vislcg3 -g lang-$LANG/src/cg3/disambiguator.cg3 | vislcg3 -g lang-$LANG/cg3/dependency.bin`

but the output structure is parsed and sent as json.
"""
line_re = r'"\<(?P<word>\w+)\>"'

def pipeline_stdout_to_json(stdout):
    out = []

    obj = {}
    for line in stdout.split("\n"):
        if line.startswith('"<'):
            obj["word"] = line[2 : -2]
        elif line.startswith("\t"):
            q1 = line.index('"') + 1
            q2 = line.index('"', q1)
            obj["root"] = line[q1 : q2]

            if "<W:" in line:
                weight_i1 = line.index("<W:", q2)
                weight_i2 = line.index(">", weight_i1)
            else:
                weight_i1 = weight_i2 = q2

            obj["props"] = line[q2 + 2 : weight_i1 - 1]
            obj["dep"] = line[weight_i2 + 2 : ]
        elif line.startswith(":"):
            out.append(obj)
            obj = {}

    if len(obj):
        out.append(obj)

    return out

# TODO!! some languages have a different pipeline!
pipeline = [
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
            "src/cg3/dependency.bin"
        ),
    ],
    pipeline_stdout_to_json
]
