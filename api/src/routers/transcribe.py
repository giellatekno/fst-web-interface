import subprocess
from enum import Enum
from typing import Union

from fastapi import APIRouter
from pydantic import BaseModel

from ..config import GTLANGS, transcriber_langs

# file built with:
# ./configure --enable-phonetic
hfst_path = "lang-{}/src/phonetics/txt2ipa.compose.hfst"

router = APIRouter(prefix = "/transcribe")

class Langs(str, Enum):
    pass

def populate_langs(en):
    class _TempEnum(str, Enum):
        pass
    _temp_enum = _TempEnum("",
        { k: k for k in transcriber_langs }
    )
    en._member_map_ = _temp_enum._member_map_
    en._member_names_ = _temp_enum._member_names_
    en._value2member_map_ = _temp_enum._value2member_map_

populate_langs(Langs)
hfst_path_for = {
    k: GTLANGS + hfst_path.format(k)
    for k in Langs.__members__
}

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

class Ok(BaseModel):
    result: list[str]

class Failure(BaseModel):
    failure: str

@router.get(
    "/{lang}/{input}",
    response_model = Union[Ok, Failure]
)
async def transcribe(lang: Langs, input: str):
    """Transcribe.
    essentially `echo "word" | hfst-lookup -q src/phonetics/txt2ipa.compose.hfst`
    """
    out = { "input": input }
    cmdline = ["hfst-lookup", "-q", hfst_path_for[lang]]

    res = subprocess.run(cmdline, input=input, text=True, capture_output=True)

    if res.stdout == "":
        out["failure"] = res.stderr
    else:
        out["result"] = parse_cmd_output(res.stdout)

    return out
