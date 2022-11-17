from fastapi import FastAPI
from .routers import generate, hyphenate
from fastapi.middleware.cors import CORSMiddleware

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

app.include_router(generate.router)
app.include_router(hyphenate.router)
