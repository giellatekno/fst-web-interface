from ..util import PartialPath

summary = "paradigm"
description = """
Generates the morphological paradigm from lemmas

`echo "$INPUT" | hfst-lookup -q lang-$LANG/src/generator-gt-norm.hfstol`

The output structure is parsed and sent as json.
"""

def pipeline_stdout_to_json(stdout):
    # TODO
    return { "result": stdout }

pipeline = [
    [
        "hfst-lookup",
        # also in conf.pl: --beam=0 (see above)
        "-q", 
        PartialPath("src/generator-gt-norm.hfstol")
    ],
    pipeline_stdout_to_json,
]


