from enum import Enum
from typing import Union

from fastapi import APIRouter
from pydantic import BaseModel

from ..toolset import generate
from ..util import (
    populate_enumlangs,
    ErrorResponse,
)

router = APIRouter(prefix = "/generate")

class GeneratorLangs(str, Enum): pass
populate_enumlangs(GeneratorLangs, generate.langs)

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
    #response_model = Union[
    #    GenerateOkResponse,
    #    ErrorResponse,
    #]
)
async def generate_handler(lang: GeneratorLangs, input: str):
    """Generate.
        essentially does `echo input | hfst-lookup -q lang/src/generator-gt-norm.hfstol`
    """
    return generate.run_pipeline(lang, input)
