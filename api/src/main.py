from enum import Enum, StrEnum
from time import time
from typing import Optional, Union, Any, TypeVar, Generic

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic.generics import GenericModel

from .toolset import tools

description = """
fst-api is the api that executes the model language applications,
for use with the fst-web-interface SPA website.
"""

app = FastAPI(
    title="fst-api",
    version="0.0.1-dev",
    description=description,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = [
        "*",
        # what else... ?
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

    expose_headers=["X-Process-Time"],
)

@app.middleware("http")
async def add_process_time_header(request, call_next):
    t0 = time()
    response = await call_next(request)
    t = time() - t0
    response.headers["X-Process-Time"] = str(time() - t0)
    return response



class LangCapabilities(BaseModel):
    date: str | None
    commit: str | None
    tools: list[str]


@app.get(
    "/capabilities",
    summary="capabilities",
    description="All languages, and their supported tools, and repository info",
    response_model=dict[str, LangCapabilities],
)
async def handle():
    out = {}
    for lang, toollist in tools.capabilities.items():
        out[lang] = { "tools": toollist }
        commithash, commitdate = tools.repos_info[lang]
        if commithash:
            out[lang]["commit"] = commithash
        if commitdate:
            out[lang]["date"] = commitdate

    return out

@app.get(
    "/capabilities/{lang}",
    summary="capabilities for language",
    description="Supported tools and repository info for a langauge",
    response_model=LangCapabilities | str,
)
async def handle(lang: str):
    out = dict()
    print(lang)
    print(tools.capabilities)
    toollist = tools.capabilities.get(lang)
    if toollist is None:
        return "no such language"
    out["tools"] = toollist

    try:
        commithash, commitdate = tools.repos_info[lang]
    except KeyError:
        pass
    else:
        out["commit"] = commithash
        out["date"] = commitdate

    return out




def _generate_route_handler(tool):
    if len(tool.langs) == 0:
        return None
    elif len(tool.langs) == 1 and tool.langs[0] == "*":
        # This tool doesn't want any GTLANGS files, which means
        # it doesn't run any of the fst programs.
        async def handler(lang: str, input: str):
            return await tool.run_pipeline(lang, input)
    else:
        Langs = StrEnum(tool.name + "Langs", tool.langs)

        async def handler(lang: Langs, input: str):
            return await tool.run_pipeline(lang, input)

    return handler


# Dynamically add routes for all tools defined in toolspecs/

class ErrorResponse(BaseModel):
    input: str
    error: str

T = TypeVar("T")
class OkResponse(GenericModel, Generic[T]):
    input: str
    result: T

for name, tool in tools.tools.items():
    url = f"/{name}/"
    url += "{lang}/{input}"

    route_handler = _generate_route_handler(tool)
    if route_handler is None:
        continue

    app.add_api_route(
        url,
        route_handler,
        response_model = Union[
            OkResponse[tool.response_model],
            ErrorResponse,
        ],
        summary = tool.summary,
        description = tool.description,
    )


