#from enum import Enum

#from pydantic import BaseModel

# no longer needed due to functional way of calling StrEnum
# requires python3.11 ..
#def populate_enumlangs(enum, langs):
#    # hack to dynamically update an Enum for use
#    # with FastAPI
#    # https://gist.github.com/myuanz/03f3e350fb165ec3697a22b559a7eb50
#    class Temp(str, Enum): pass
#    temp = Temp("", { k: k for k in langs })
#    enum._member_map_ = temp._member_map_
#    enum._member_names_ = temp._member_names_
#    enum._value2member_map_ = temp._value2member_map_


# just used one place: in main.py, so just defined there
#class ErrorResponse(BaseModel):
#    input: str
#    error: str


class PartialPath:
    def __init__(self, p):
        self.p = p
