from pydantic import BaseModel
from ..util import PartialPath

summary = "digit2text"
description = """
Generate number words from arabic numerals, like 1 -> "one", 8 -> "eight", 22 -> "twenty two", ...

`echo "$INPUT" | hfst-lookup lang-$LANG/src/transcriptions/transcriptor-numbers-digit2text.filtered.lookup.hfstol`

The output structure is parsed and sent as json.
"""

# Cannot be named "Response" (fastapi or something gets confused)
class ResponseOut(BaseModel):
    number: int
    answers: list

def pipeline_stdout_to_json(stdout) -> ResponseOut:
    # "23\ttjuetre\t0,000000\n23\ttreogtjue\t0,000000\n\n"
    out = { "number": None, "answers": [] }
    for line in stdout.split("\n"):
        answers = []
        if line.strip() == "":
            continue

        splits = line.split("\t")
        if len(splits) != 3:
            # TODO print debug/warning in logs?
            continue

        n, number_as_text, _weights = splits
        out["number"] = n
        out["answers"].append(number_as_text)

    return out

pipeline = [
    [
        "hfst-lookup",
        PartialPath(
            "src/transcriptions/transcriptor-numbers-digit2text.filtered.lookup.hfstol"
        ),
    ],
    pipeline_stdout_to_json
]
