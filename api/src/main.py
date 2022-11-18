from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import capabilities
from .routers import (
    generate,
    hyphenate,
    transcribe,
)

origins = [
    "*",
    #"http://localhost:5173",
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/capabilities")
async def handle():
    return capabilities

app.include_router(generate.router)
app.include_router(hyphenate.router)
app.include_router(transcribe.router)
