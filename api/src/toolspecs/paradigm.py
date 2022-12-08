from ..util import PartialPath

summary = "paradigm"
description = """
Generates the morphological paradigm from lemmas

`echo "$INPUT" | hfst-lookup -q lang-$LANG/src/generator-gt-norm.hfstol`

The output structure is parsed and sent as json.
"""

# echo word | analyze

def pipeline_stdout_to_json(stdout):
    return { "result": stdout }

pipeline = [
    [
        "hfst-tokenize",
        "-q", "--beam=0",
        PartialPath("tools/tokenisers/tokeniser-disamb-gt-desc.pmhfst"),
    ],
    [
        "hfst-lookup",
        "-q", "--beam=0",
        PartialPath("src/analyser-gt-desc.hfstol"),
    ],
    pipeline_stdout_to_json,
]


