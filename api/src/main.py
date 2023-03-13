from enum import StrEnum
from time import time
import inspect
from typing import Union, TypeVar, Generic

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic.generics import GenericModel
from makefun import with_signature

from .toolset import tools

T = TypeVar("T")
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

    expose_headers=["X-Process-Time"],
)


@app.middleware("http")
async def add_process_time_header(request, call_next):
    t0 = time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time() - t0)
    return response


class ErrorResponse(BaseModel):
    input: str
    error: str


class OkResponse(GenericModel, Generic[T]):
    input: str
    result: T


class LangCapabilities(BaseModel):
    tools: list[str]
    repo_info: dict[str, str]


@app.get(
    "/capabilities",
    summary="capabilities",
    description="All languages, their supported tools, and repository info",
    response_model=dict[str, dict[str, LangCapabilities]],
)
async def handle_capabilities():
    return {"result": tools.capabilities()}


@app.get(
    "/capabilities/{lang}",
    summary="capabilities for language",
    description="Supported tools and repository info for a langauge",
    response_model=LangCapabilities,
)
async def handle_capabilities_for_lang(lang: str):
    return tools.capabilities()[lang]


def _generate_route_handler(tool):
    if len(tool.langs) == 0:
        return None
    else:
        Langs = StrEnum(tool.name + "Langs", tool.langs)

        query_params = {}
        for name, desc in tool.query_params.items():
            query_params[name] = Query()

        async def fn(lang: Langs, input: str):
            pass

        # extract the signature as we have it, and update it
        signature = inspect.signature(fn)
        new_signature = signature.replace(
            parameters=(
                *signature.parameters.values(),
                *[
                    inspect.Parameter(
                        name,
                        kind=inspect.Parameter.KEYWORD_ONLY,
                        default=Query(
                            default=..., description=param["description"]
                        ),
                        annotation=param["type"],
                    )
                    for name, param in tool.query_params.items()
                ]
            ),
        )

        # finally re-make the function, now with the apporopriate signature
        @with_signature(new_signature, func_name="handler")
        async def handler(*args, **kwargs):
            # here we must also do some tricks to get the actual parameters
            actual_query_params = {name: kwargs[name] for name in query_params}
            lang = kwargs["lang"]
            input = kwargs["input"]
            resp = await tool.run_pipeline(
                    lang, input, query_params=actual_query_params)
            return resp

    return handler


# Dynamically add routes for all tools defined in toolspecs/


for name, tool in tools.tools.items():
    url = f"/{name}/"
    url += "{lang}/{input}"

    route_handler = _generate_route_handler(tool)
    if route_handler is None:
        continue

    app.add_api_route(
        url,
        route_handler,
        response_model=Union[
            OkResponse[tool.response_model],
            ErrorResponse,
        ],
        summary=tool.summary,
        description=tool.description,
    )
