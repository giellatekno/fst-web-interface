import subprocess
from enum import Enum
from typing import Union

from fastapi import APIRouter
from pydantic import BaseModel

from ..config import GTLANGS, generator_langs

router = APIRouter(
    prefix = "/generate"
)

class GeneratorLangs(str, Enum):
    pass

def populate_generator_langs(gl):
    # hack to dynamically update an Enum for use with FastAPI
    # https://gist.github.com/myuanz/03f3e350fb165ec3697a22b559a7eb50
    class _TempEnum(str, Enum):
        pass

    _temp_enum = _TempEnum("", { k: k for k in generator_langs })
    gl._member_map_ = _temp_enum._member_map_
    gl._member_names_ = _temp_enum._member_names_
    gl._value2member_map_ = _temp_enum._value2member_map_

populate_generator_langs(GeneratorLangs)
hfstol_path = "lang-{}/src/generator-gt-norm.hfstol"
hfstol_path_for = {
    k: GTLANGS + hfstol_path.format(k)
    for k in GeneratorLangs.__members__
}

#def get_generate_cmdline(lang):
#    hfstol = GTLANGS + "lang-!!{}/src/generator-gt-norm.hfstol".format(lang)
#    # hacky..
#    hfstol = hfstol.replace("!!.", "")
#    return ["hfst-lookup", "-q", hfstol]

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

class GenerateResponseBase(BaseModel):
    input: str

class GenerateResponseFound(GenerateResponseBase):
    found: str

class GenerateResponseNotFound(GenerateResponseBase):
    not_found: str

class GenerateResponseError(GenerateResponseBase):
    error: str

class Ok(BaseModel):
    result: GenerateResponseFound | GenerateResponseNotFound | GenerateResponseError

class Failure(BaseModel):
    failure: str

@router.get(
    "/{lang}/{input}",
    response_model = Union[Ok, Failure]
)
async def generate(lang: GeneratorLangs, input: str):
    """Generate.
        essentially does `echo input | hfst-lookup -q lang/src/generator-gt-norm.hfstol`
    """
    out = { "input": input }
    cmdline = ["hfst-lookup", "-q", hfstol_path_for[lang]]
    res = subprocess.run(cmdline, input=input, text=True, capture_output=True)

    if res.stdout == "":
        out["failure"] = res.stderr
    else:
        out["result"] = parse_cmd_output(res.stdout)

    return out
