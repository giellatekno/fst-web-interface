from enum import StrEnum
from time import time
import inspect
from typing import Union, TypeVar, Generic
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic.generics import GenericModel
from makefun import with_signature

from .toolset import tools

VERSION = "0.0.1-dev"

T = TypeVar("T")
description = """
fst-api is a web api that executes various language model pipelines,
for use with the fst-web-interface SPA website.
"""


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


@asynccontextmanager
async def lifespan(app):
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

    print("Available tools per language:")
    for lang, tool in tools.tools.items():
        print(f"{lang}: {', '.join(tool.langs)}")
        pass

    # yield marks the point where startup ends and shutdown begins
    # anything before yield happens on startup, anything after it happens
    # on shutdown
    yield


app = FastAPI(
    title="fst-api",
    version=VERSION,
    description=description,
    contact={
        "name": "Giellatekno",
        "url": "https://giellatekno.uit.no",
        "email": "giellatekno@uit.no",
    },
    lifespan=lifespan,
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


@app.get("/version", summary="version of the api")
async def handle_version():
    return {"result": VERSION}


@app.get(
    "/capabilities",
    summary="capabilities",
    description="All languages, their supported tools, and repository info",
    response_model=dict[str, dict[str, LangCapabilities]],
)
async def handle_capabilities():
    return {"result": tools.capabilities()}


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html><head><title>fst-api</title></head>
    <body style="display:flex;justify-content:center">
        <div style="display: flex; flex-direction: column;">
        <h3>fst-api</h3>
        <p>&nbsp;&nbsp;Giellatekno, UiT</p>
        <p>This is the root. Nothing to see here.</p>
        <p>explore the api using either</p>
        <div>
            <a href="/docs">/docs</a>
            or
            <a href="/redoc">/redoc</a>
        </div>
        </div>
    </body>
    </html>
    """


@app.get(
    "/capabilities/{lang}",
    summary="capabilities for language",
    description="Supported tools and repository info for a langauge",
    response_model=LangCapabilities,
)
async def handle_capabilities_for_lang(lang: str):
    return tools.capabilities()[lang]


