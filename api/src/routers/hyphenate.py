import subprocess
from enum import Enum
from typing import Union

from fastapi import APIRouter
from pydantic import BaseModel

from ..config import GTLANGS, hyphenate_langs
from ..util import (
    populate_enumlangs,
    run_cmdline,
    progout_to_response,
    ErrorResponse,
)

router = APIRouter(prefix = "/hyphenate")

class HyphenateLangs(str, Enum): pass
populate_enumlangs(HyphenateLangs, hyphenate_langs)

cmd_chain_for = {}
for lang in hyphenate_langs:
    cmd_chain_for[lang] = [
        [
            "hfst-lookup",
            "-q",
            GTLANGS / f"lang-{lang}" / "tools" / "hyphenators" / "hyphenator-gt-desc.hfstol"
        ]
    ]

def parse_cmd_output(output):
    output = output.strip()
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

class HyphenateOkResponse(BaseModel):
    input: str
    result: list[str]

@router.get(
    "/{lang}/{input}",
    response_model = Union[
        HyphenateOkResponse,
        ErrorResponse,
    ]
)
async def hyphenate(lang: HyphenateLangs, input: str):
    """Hyphenate.
    essentially does `echo "konspirasjon" | hfst-lookup lang-xxx/tools/hyphenators/hyphenator-gt-desc.hfstol`
    """
    next_input = input
    for prog in cmd_chain_for[lang]:
        res = run_cmdline(prog, next_input)
        next_input = res.stdout

    return progout_to_response(input, res, parse_cmd_output)
