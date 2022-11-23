from ..util import PartialPath

def pipeline_stdout_to_json(stdout):
    output = stdout.strip()
    #{'input': 'konspirasjon', 'result': []}}
    out = set()
    lines = output.split("\n")
    for line in lines:
        splits = line.strip().split("\t")
        if len(splits) != 3:
            continue
        else:
            given, result, weight = splits

            # TODO koffer står det # på noen av og til?
            result = result.replace("#", "-")

            out.add(result)

    return list(out)

pipeline = [
    [
        "hfst-lookup",
        "-q",
        PartialPath(
            "tools/hyphenators/hyphenator-gt-desc.hfstol"
        )
    ],
    pipeline_stdout_to_json
]
