from enum import Enum
from typing import Union

from fastapi import APIRouter
from pydantic import BaseModel

from ..toolset import hyphenate
from ..util import (
    populate_enumlangs,
    ErrorResponse,
)

router = APIRouter(prefix = "/hyphenate")

class HyphenateLangs(str, Enum): pass
populate_enumlangs(HyphenateLangs, hyphenate.langs)

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
async def hyphenate_handler(lang: HyphenateLangs, input: str):
    """Hyphenate.
    essentially does `echo "konspirasjon" | hfst-lookup lang-xxx/tools/hyphenators/hyphenator-gt-desc.hfstol`
    """
    return hyphenate.run_pipeline(lang, input)
