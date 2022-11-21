import subprocess
from enum import Enum
from typing import Union

from fastapi import APIRouter
from pydantic import BaseModel

from ..config import (
    GTLANGS,
    generator_langs,
)
from ..util import (
    populate_enumlangs,
    run_cmdline,
    progout_to_response,
    ErrorResponse,
)

router = APIRouter(
    prefix = "/generate"
)

class GeneratorLangs(str, Enum): pass
populate_enumlangs(GeneratorLangs, generator_langs)

cmd_chain_for = {}
for lang in generator_langs:
    cmd_chain_for[lang] = [
        [
            "hfst-lookup",
            "-q",
            GTLANGS / f"lang-{lang}" / "src" / "generator-gt-norm.hfstol",
        ]
    ]

def parse_cmd_output(output):
    splits = output.strip().split("\t")
    out = {}
    if len(splits) != 3:
        out["error"] = output
    else:
        given, result, weight = splits
        out["input"] = given
        if weight == "inf":
            out["not_found"] = result
        else:
            out["found"] = result
    return out

class GenerateResponseFound(BaseModel):
    found: str

class GenerateResponseNotFound(BaseModel):
    not_found: str

class GenerateResponseError(BaseModel):
    error: str

class GenerateOkResponse(BaseModel):
    input: str
    result: GenerateResponseFound | GenerateResponseNotFound | GenerateResponseError

@router.get(
    "/{lang}/{input}",
    response_model = Union[
        GenerateOkResponse,
        ErrorResponse,
    ]
)
async def generate(lang: GeneratorLangs, input: str):
    """Generate.
        essentially does `echo input | hfst-lookup -q lang/src/generator-gt-norm.hfstol`
    """
    next_input = input
    for prog in cmd_chain_for[lang]:
        print(prog)
        res = run_cmdline(prog, next_input)
        next_input = res.stdout

    return progout_to_response(input, res, parse_cmd_output)
