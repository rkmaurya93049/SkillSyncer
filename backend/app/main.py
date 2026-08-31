import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db.init_db import init_db
from .routers import evaluation, upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure the SQLite schema exists in clean/containerized deployments.
    init_db()
    yield


app = FastAPI(
    title="SkillSyncer Resume Relevance API",
    version="0.2.0",
    description="Resume parsing, relevance scoring, history, and improvement suggestions.",
    lifespan=lifespan,
)

raw_origins = os.getenv("CORS_ORIGINS", "*")
allow_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
if not allow_origins:
    allow_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(evaluation.router)


@app.get("/")
def root():
    return {
        "name": "SkillSyncer Resume Relevance API",
        "status": "running",
        "health": "/health",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
