from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import upload
from routers import evaluation

app = FastAPI(title="Resume Relevance MVP", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(evaluation.router)

@app.get("/health")
def health():

    return {"status": "ok"}
