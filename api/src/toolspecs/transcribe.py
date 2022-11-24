from ..util import PartialPath

summary = "transcribe"
description = """
Get the IPA (International Phonetic Alphabet) representation of a word (or several?).

Like running `echo "$INPUT" | hfst-lookup lang-$LANG/src/phonetics/txt2ipa.compose.hfst`,

but the output structure is parsed and sent as json.
"""

def pipeline_stdout_to_json(stdout):
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

        # built with: ./configure --enable-phonetic --enable-tts
        PartialPath(
            "src/phonetics/txt2ipa.compose.hfst"
        )
    ],
    pipeline_stdout_to_json
]
