from pydantic import BaseModel
from ..util import PartialPath

summary = "generate"
description = """
Generates normative wordforms from lemma + morphological tags.

`echo "$INPUT" | hfst-lookup src/generator-gt-norm.hfstol`,

The output structure is parsed and sent as json.
"""

class Response(BaseModel):
    input: str
    not_found: str | None
    found: str | None
    error: str | None

def pipeline_stdout_to_json(stdout) -> Response:
    splits = stdout.strip().split("\t")
    out = {}
    if len(splits) != 3:
        out["error"] = stdout
    else:
        given, result, weight = splits
        out["input"] = given
        if weight == "inf":
            out["not_found"] = result
        else:
            out["found"] = result
    return out

pipeline = [
    [
        "hfst-lookup",
        "-q",
        PartialPath("src/generator-gt-norm.hfstol"),
    ],
    pipeline_stdout_to_json
]
