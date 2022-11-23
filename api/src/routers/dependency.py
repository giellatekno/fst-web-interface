from enum import Enum
from typing import Union

from fastapi import APIRouter
from pydantic import BaseModel

from ..toolset import dependency
from ..util import (
    populate_enumlangs,
    ErrorResponse,
)

router = APIRouter(prefix = "/dependency")

class DependencyLangs(str, Enum): pass
populate_enumlangs(DependencyLangs, dependency.langs)

# TODO
class DependencyOkResponse(BaseModel):
    input: str
    result: list[str]

@router.get(
    "/{lang}/{input}",
    # TODO
    #response_model = Union[
    #    DependencyOkResponse,
    #    ErrorResponse,
    #]
)
async def dependency_handler(lang: DependencyLangs, input: str):
    """Dependency.
    Basically `...`
    """
    return dependency.run_pipeline(lang, input)
