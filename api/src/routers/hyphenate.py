import subprocess
from enum import Enum
from typing import Union

from fastapi import APIRouter
from pydantic import BaseModel

from ..config import GTLANGS, hyphenator_langs

router = APIRouter(
    prefix = "/hyphenate"
)

class HyphenatorLangs(str, Enum):
    pass

def populate_hyphenator_langs(gl):
    # hack to dynamically update an Enum for use with FastAPI
    # https://gist.github.com/myuanz/03f3e350fb165ec3697a22b559a7eb50
    class _TempEnum(str, Enum):
        pass

    _temp_enum = _TempEnum("", { k: k for k in hyphenator_langs })
    gl._member_map_ = _temp_enum._member_map_
    gl._member_names_ = _temp_enum._member_names_
    gl._value2member_map_ = _temp_enum._value2member_map_

populate_hyphenator_langs(HyphenatorLangs)
hfstol_path = "lang-{}/tools/hyphenators/hyphenator-gt-desc.hfstol"
hfstol_path_for = {
    k: GTLANGS + hfstol_path.format(k)
    for k in HyphenatorLangs.__members__
}

def parse_cmd_output(output):
    output = output.strip()
    #{'input': 'konspirasjon', 'result': {'results': []}}
    out = set()
    if "\n" in output:
        lines = output.split("\n")

        for line in lines:
            splits = line.strip().split("\t")
            if len(splits) != 3:
                print(splits)
                continue
                #out["error"] = output
            else:
                given, result, weight = splits

                # TODO koffer står det # på noen av og til?
                result = result.replace("#", "-")

                out.add(result)
                #if weight == "inf":
                    #out["not_found"] = result
    else:
        # får alltid stavelse, selv om input ikke er et
        # ordentlig ord, fordi det går bare på "regler",
        # ikke sant?
        print("unreachable?")

    return list(out)

class HyphenateResponseBase(BaseModel):
    input: str

class HyphenateResponseFound(HyphenateResponseBase):
    results: list[str]

class HyphenateResponseNotFound(HyphenateResponseBase):
    not_found: str

class HyphenateResponseError(HyphenateResponseBase):
    error: str

class Ok(BaseModel):
    result: list[str]

class Failure(BaseModel):
    failure: str

@router.get(
    "/{lang}/{input}",
    response_model = Union[Ok, Failure]
)
async def hyphenate(lang: HyphenatorLangs, input: str):
    """Hyphenate.
    essentially does `echo "konspirasjon" | hfst-lookup lang-xxx/tools/hyphenators/hyphenator-gt-desc.hfstol`
    """
    out = { "input": input }
    cmdline = ["hfst-lookup", "-q", hfstol_path_for[lang]]
    res = subprocess.run(cmdline, input=input, text=True, capture_output=True)

    if res.stdout == "":
        out["failure"] = res.stderr
    else:
        out["result"] = parse_cmd_output(res.stdout)

    print(out)
    return out
