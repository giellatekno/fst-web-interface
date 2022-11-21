from enum import Enum
from typing import Union

from fastapi import APIRouter
from pydantic import BaseModel

from ..config import GTLANGS, disamb_langs
from ..util import (
    run_cmdline,
    progout_to_response,
    populate_enumlangs,
)

router = APIRouter(prefix = "/disambiguate")

class DisambiguateLangs(str, Enum): pass
populate_enumlangs(DisambiguateLangs, disamb_langs)

cmd_chain_for = {}
for lang in disamb_langs:
    cmd_chain_for[lang] = [
        [
            "hfst-tokenize",
            "-cg",
            GTLANGS / f"lang-{lang}" / "tools" / "tokenisers" / "tokeniser-disamb-gt-desc.pmhfst"
        ],
        [
            "vislcg3",
            "-g",
            GTLANGS / f"lang-{lang}" / "src" / "cg3" / "disambiguator.cg3",
        ]
    ]

class DisambLineResult(BaseModel):
    root_word: str | None
    classes: str | None

class DisambLine(BaseModel):
    input_word: str
    input_word_result: list[DisambLineResult]

class DisambOkResponse(BaseModel):
    input: str
    result: list[str] | None

class ErrorResponse(BaseModel):
    input: str
    error: str

def disamb_out_to_response(stdout):
    out = []
    #{ input_word, input_word_result },
    # where input_word_result = {
    #   root_word, classes }

    for line in stdout.split("\n"):
        line = line.strip()

        if line == "":
            continue
        elif line.startswith("\"<"):
            input_word = line[2:-2]
            word_disambs = []
        elif line == ":":
                out.append({
                    "input_word": input_word,
                    "word_disambs": word_disambs
                })
        else:
            q1 = line.index('"') + 1
            q2 = line.index('"', q1)
            root_word = line[q1:q2]
            w_ind = line.index("<")
            classes = line[q2 + 2 : w_ind - 1]

            word_disambs.append({
                "root_word": root_word,
                "classes": classes,
            })
    out.append({
        "input_word": input_word,
        "word_disambs": word_disambs,
    })

    return out

@router.get(
    "/{lang}/{input}",
    # TODO fix response model
    #response_model = Union[
    #    DisambOkResponse,
    #    ErrorResponse,
    #]
)
async def disambiguate(
    lang: DisambiguateLangs,
    input: str
):
    """Disambiguate.
    like `echo input | hfst-tokenize -cg lang/tokeniser-disamb-gt-desc.pmhfst | vislcg3 -g lang/disambiguator.cg3`
    """
    next_input = input
    for prog in cmd_chain_for[lang]:
        res = run_cmdline(prog, next_input)
        next_input = res.stdout

    return progout_to_response(input, res, disamb_out_to_response)

