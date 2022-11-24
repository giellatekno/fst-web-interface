from typing import Optional, Union, Any

from pydantic import BaseModel
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
)
async def handle():
    return tools.capabilities


# dynamically add all routes
# this could use more love, like automatically
# create enums for the inputs, to not just accept strings
# see https://stackoverflow.com/questions/73291228/add-route-to-fastapi-with-custom-path-parameters

# with this, I could basically delete all routes/* ...

class ErrorResponse(BaseModel):
    input: str
    error: str

for name, tool in tools.tools.items():
    def generate_route_handler(tool):
        def handler(lang, input):
            return tool.run_pipeline(lang, input)
        return handler

    url = f"/{name}/"
    url += "{lang}/{input}"

    app.add_api_route(
        url,
        generate_route_handler(tool),
        response_model = Union[ErrorResponse, Any],
        summary=tool.summary,
        description=tool.description,
    )

