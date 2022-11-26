from typing import Optional, Union, Any, TypeVar, Generic
from enum import Enum, StrEnum

from pydantic import BaseModel
from pydantic.generics import GenericModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

    # TODO for timing request time taken
    expose_headers=["X-Process-Time"],
)



@app.get(
    "/capabilities",
    summary="capabilities",
    description="Which tools are available for which languages",
    response_model=dict[str, list[str]],
)
async def handle():
    return tools.capabilities




def _generate_route_handler(tool):
    if "*" in tool.pipeline_for:
        # This tool doesn't want any GTLANGS files, which means
        # it doesn't run any of the fst programs.
        async def handler(lang: str, input: str):
            return await tool.run_pipeline(lang, input)
    else:
        if len(tool.pipeline_for) == 0:
            # No languages had all required files for this tool
            return None

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


