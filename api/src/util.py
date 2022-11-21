from subprocess import run
from enum import Enum

from pydantic import BaseModel

def run_cmdline(cmdline, input):
    return run(cmdline, input=input, text=True, capture_output=True)

def progout_to_response(input, res, convert):
    """Takes a subprocess.run()-result, and converts
    it into the required result"""
    out = { "input": input }
    if res.stdout == "":
        out["error"] = res.stderr
    else:
        out["result"] = convert(res.stdout)
    return out

def populate_enumlangs(enum, langs):
    # hack to dynamically update an Enum for use
    # with FastAPI
    # https://gist.github.com/myuanz/03f3e350fb165ec3697a22b559a7eb50
    class Temp(str, Enum): pass
    temp = Temp("", { k: k for k in langs })
    enum._member_map_ = temp._member_map_
    enum._member_names_ = temp._member_names_
    enum._value2member_map_ = temp._value2member_map_


class ErrorResponse(BaseModel):
    input: str
    error: str
