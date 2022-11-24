from ..util import PartialPath

summary = "num"
description = """
Get a textual representation of how to say a number. Like 1 -> "one", 8 -> "eight", 22 -> "twenty two", ...

Like running `echo "$INPUT" | hfst-lookup lang-$LANG/src/transcriptions/transcriptor-numbers-digit2text.filtered.lookup.hfstol`

but the output structure is parsed and sent as json.
"""

def pipeline_stdout_to_json(stdout):
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
