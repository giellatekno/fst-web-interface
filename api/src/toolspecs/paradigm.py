from ..util import PartialPath

def pipeline_stdout_to_json(stdout):
    # TODO
    return { "result": stdout }

pipeline = [
    [
        "hfst-tokenize",
        # also in conf.pl: --beam=0 (result filtering?)
        "-q", 
        
        PartialPath(
            # built with: ./configure --enable-tokenisers
            "tools/tokenisers/tokeniser-disamb-gt-desc.pmhfst",
        )
    ],
    [
        "hfst-lookup",
        # also in conf.pl: --beam=0 (see above)
        "-q", 
        PartialPath("src/analyser-gt-desc.hfstol")
    ],
    pipeline_stdout_to_json,
]


