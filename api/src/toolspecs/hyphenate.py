from ..util import PartialPath

summary = "hyphenate"
description = """
Put dashes in between each syllable of a word.

`echo "$INPUT" | hfst-lookup tools/hyphenators/hyphenators-gt-desc.hfstol`

Output is structured up as json.
"""


def pipeline_stdout_to_json(stdout) -> list[str]:
    # {'input': 'konspirasjon', 'result': []}}
    out = []
    for line in stdout.strip().split("\n"):
        try:
            given, result, weight = line.strip().split("\t")

            # TODO koffer står det # på noen av og til?
            result = result.replace("#", "-")

            out.append(result)
        except ValueError:
            # line was not 3 columns, so just ignore it
            pass

    return out


pipeline = [
    [
        "hfst-lookup",
        "-q",
        PartialPath(
            # --enable-fst-hyphenator
            "tools/hyphenators/hyphenator-gt-desc.hfstol"
        )
    ],
    pipeline_stdout_to_json
]
