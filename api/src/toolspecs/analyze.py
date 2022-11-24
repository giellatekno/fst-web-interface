from ..util import PartialPath

summary = "analyze"
description = """
Short description here.

Like running `echo "$INPUT" | ...?`

but the output structure is parsed and sent as json.
"""

def pipeline_stdout_to_json(stdout):
    pass

pipeline = [
    [
        "echo",
        "TODO",
    ],
    pipeline_stdout_to_json
]
