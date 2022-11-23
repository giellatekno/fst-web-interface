from enum import Enum
from typing import Union

from fastapi import APIRouter
from pydantic import BaseModel

from ..toolset import num
from ..util import (
    populate_enumlangs,
    ErrorResponse,
)

router = APIRouter(prefix = "/num")

class NumLangs(str, Enum): pass
populate_enumlangs(NumLangs, num.langs)

# TODO
class NumOkResponse(BaseModel):
    input: str
    result: list[str]

@router.get(
    "/{lang}/{input}",
    # TODO
    #response_model = Union[
    #    NumOkResponse,
    #    ErrorResponse,
    #]
)
async def num_handler(lang: NumLangs, input: str):
    """Num.
    Basically `hfst-lookup ...`
    """
    return num.run_pipeline(lang, input)
