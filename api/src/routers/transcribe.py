import subprocess
from enum import Enum
from typing import Union

from fastapi import APIRouter
from pydantic import BaseModel

from ..config import GTLANGS, transcriber_langs
from ..util import (
    populate_enumlangs,
    run_cmdline,
    progout_to_response,
    ErrorResponse,
)

# file built with:
# lang-xxx/src/phonetics/txt2ipa.compose.hfst
# ./configure --enable-phonetic

router = APIRouter(prefix = "/transcribe")

class TranscribeLangs(str, Enum): pass
populate_enumlangs(TranscribeLangs, transcriber_langs)

cmd_chain_for = {}
for lang in transcriber_langs:
    cmd_chain_for[lang] = [
        [
            "hfst-lookup",
            "-q",
            GTLANGS / f"lang-{lang}" / "src" / "phonetics" / "txt2ipa.compose.hfst"
        ],
    ]

def parse_cmd_output(output):
    lines = output.strip().split("\n")
    out = []
    for line in lines:
        splits = line.split("\t")
        if len(splits) != 3:
            continue
        word, result, weight = splits
        out.append(result)

    return out

class TranscribeOkResponse(BaseModel):
    result: list[str]

@router.get(
    "/{lang}/{input}",
    response_model = Union[
        TranscribeOkResponse,
        ErrorResponse,
    ]
)
async def transcribe(
    lang: TranscribeLangs,
    input: str,
):
    """Transcribe.
    essentially `echo "word" | hfst-lookup -q src/phonetics/txt2ipa.compose.hfst`
    """
    next_input = input
    for prog in cmd_chain_for[lang]:
        res = run_cmdline(prog, next_input)
        next_input = res.stdout

    return progout_to_response(input, res, parse_cmd_output)
