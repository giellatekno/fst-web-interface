from ..langmodel_file import TXT2IPA_COMPOSE_HFST

summary = "transcribe"
description = """
Converts orthography into IPA

`echo "$INPUT" | hfst-lookup lang-$LANG/src/phonetics/txt2ipa.compose.hfst`,

The output structure is parsed and sent as json.
"""


def pipeline_stdout_to_json(stdout) -> list[str]:
    lines = stdout.strip().split("\n")
    out = []
    for line in lines:
        splits = line.split("\t")
        if len(splits) != 3:
            continue
        word, result, weight = splits
        out.append(result)

    return out


pipeline = [
    [
        "hfst-lookup",
        "-q",
        TXT2IPA_COMPOSE_HFST,
    ],
    pipeline_stdout_to_json
]
