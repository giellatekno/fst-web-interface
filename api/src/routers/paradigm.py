from enum import Enum
from typing import Union

from fastapi import APIRouter
from pydantic import BaseModel

from ..toolset import paradigm
from ..util import (
    populate_enumlangs,
    ErrorResponse,
)

router = APIRouter(prefix = "/paradigm")

class ParadigmLangs(str, Enum): pass
populate_enumlangs(ParadigmLangs, paradigm.langs)

# TODO response_model classes here

@router.get(
    "/{lang}/{input}",
    # TODO
    #response_model = Union[ ... ]
)
async def paradigm_handler(
    lang: ParadigmLangs,
    input: str,
):
    """Paradigm.
    """
    return paradigm.run_pipeline(lang, input)

