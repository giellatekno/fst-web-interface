from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import capabilities
from .routers import (
    generate,
    hyphenate,
    transcribe,
    disambiguate,
    paradigm,
)

app = FastAPI()
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

@app.get("/capabilities")
async def handle():
    return capabilities

app.include_router(generate.router)
app.include_router(hyphenate.router)
app.include_router(transcribe.router)
app.include_router(disambiguate.router)
app.include_router(paradigm.router)
