from enum import Enum
from typing import Union

from fastapi import APIRouter
from pydantic import BaseModel

from ..toolset import disambiguate
from ..util import (
    populate_enumlangs,
    ErrorResponse,
)

router = APIRouter(prefix = "/disambiguate")

class DisambiguateLangs(str, Enum): pass
populate_enumlangs(DisambiguateLangs, disambiguate.langs)

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

@router.get(
    "/{lang}/{input}",
    # TODO fix response model
    #response_model = Union[
    #    DisambOkResponse,
    #    ErrorResponse,
    #]
)
async def disambiguate_handler(
    lang: DisambiguateLangs,
    input: str
):
    """Disambiguate.
    like `echo input | hfst-tokenize -cg lang/tokeniser-disamb-gt-desc.pmhfst | vislcg3 -g lang/disambiguator.cg3`
    """
    return disambiguate.run_pipeline(lang, input)
