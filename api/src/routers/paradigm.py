from enum import Enum
from typing import Union

from fastapi import APIRouter
from pydantic import BaseModel

from ..config import GTLANGS, paradigm_langs
from ..util import (
    run_cmdline,
    progout_to_response,
    populate_enumlangs,
)

router = APIRouter(prefix = "/paradigm")

class ParadigmLangs(str, Enum): pass
populate_enumlangs(ParadigmLangs, paradigm_langs)

cmd_chain_for = {}
for lang in paradigm_langs:
    cmd_chain_for[lang] = [
        [
            "hfst-tokenize",
            "-q", # also in conf.pl: --beam=0 (result filtering?)
            
            # built with --enable-tokenisers
            GTLANGS / f"lang-{lang}" / "tools" / "tokenisers" / "tokeniser-disamb-gt-desc.pmhfst"
        ],
        [
            "hfst-lookup",
            "-q", # also in conf.pl: --beam=0 (see above)
            GTLANGS / f"lang-{lang}" / "src" / "analyser-gt-desc.hfstol"
        ]
    ]

# TODO response_model classes here

def pipeline_output_to_json(stdout):
    return { "result": stdout }

@router.get(
    "/{lang}/{input}",
    # TODO
    #response_model = Union[ ... ]
)
async def paradigm(
    lang: ParadigmLangs,
    input: str,
):
    """Paradigm.
    """
    next_input = input
    for prog in cmd_chain_for[lang]:
        res = run_cmdline(prog, next_input)
        next_input = res.stdout

    return progout_to_response(
        input,
        res,
        pipeline_output_to_json,
    )

