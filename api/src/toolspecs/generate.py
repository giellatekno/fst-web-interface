from ..util import PartialPath

def pipeline_stdout_to_json(stdout):
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
