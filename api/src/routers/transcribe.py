from enum import Enum
from typing import Union

from fastapi import APIRouter
from pydantic import BaseModel

from ..toolset import transcribe
from ..util import (
    populate_enumlangs,
    ErrorResponse,
)

router = APIRouter(prefix = "/transcribe")

class TranscribeLangs(str, Enum): pass
populate_enumlangs(TranscribeLangs, transcribe.langs)

class TranscribeOkResponse(BaseModel):
    result: list[str]

@router.get(
    "/{lang}/{input}",
    response_model = Union[
        TranscribeOkResponse,
        ErrorResponse,
    ]
)
async def transcribe_handler(
    lang: TranscribeLangs,
    input: str,
):
    """Transcribe.
    essentially `echo "word" | hfst-lookup -q src/phonetics/txt2ipa.compose.hfst`
    """
    return transcribe.run_pipeline(lang, input)
