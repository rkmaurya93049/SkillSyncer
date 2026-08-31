---
title: SkillSyncer API
emoji: 📄
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# SkillSyncer / RelevAI — Resume Relevance Checker

A full-stack resume-evaluation project that compares resumes with job descriptions, calculates relevance scores, stores evaluation history, and generates improvement suggestions.

## Architecture

```text
Streamlit frontend
      |
      | HTTP / multipart uploads
      v
FastAPI backend (Hugging Face Docker Space)
      |
      +-- PDF/DOCX parsing
      +-- rule-based requirement matching
      +-- MiniLM semantic similarity
      +-- weighted relevance scoring
      +-- Gemini-powered suggestions (optional fallback available)
      +-- SQLite evaluation history
```

## Repository Structure

```text
SkillSyncer/
├── Dockerfile                  # Hugging Face Docker Space backend
├── .dockerignore
├── backend/
│   ├── .env.example
│   ├── requirements-hf.txt     # Minimal HF runtime dependencies
│   └── app/
│       ├── main.py             # FastAPI entry point
│       ├── db/
│       ├── models/
│       ├── routers/
│       ├── services/
│       └── requirements.txt    # Full development dependencies
├── frontend/
│   ├── components/
│   ├── dashboard.py            # Streamlit frontend
│   └── requirements.txt
└── README.md
```

## Backend API

When running, useful endpoints are:

- `GET /` — API information
- `GET /health` — health check
- `GET /docs` — interactive FastAPI/OpenAPI documentation
- `POST /evaluate/` — evaluate a resume against a JD
- `GET /evaluate/history` — evaluation history
- `GET /evaluate/{id}` — evaluation details
- `GET /evaluate/export/json` — JSON export
- `GET /evaluate/export/csv` — CSV export
- `POST /upload/jd` — inspect/structure a JD

## Local Development

### Backend

Run from the repository root so package imports are consistent with production:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install the backend dependencies:

```bash
pip install -r backend/app/requirements.txt
```

Copy the environment template and add your key:

```bash
cp backend/.env.example .env
```

Start FastAPI:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
pip install -r requirements.txt
```

Point the frontend to the backend if needed:

Windows PowerShell:

```powershell
$env:SKILLSYNCER_API_URL="http://localhost:8000"
streamlit run dashboard.py
```

macOS/Linux:

```bash
export SKILLSYNCER_API_URL="http://localhost:8000"
streamlit run dashboard.py
```

If `SKILLSYNCER_API_URL` is not set, the frontend defaults to the existing SkillSyncer Hugging Face backend URL.

## Deploy Backend on Hugging Face Spaces

The repository is prepared for a **Docker Space**. Hugging Face exposes the application on port `7860`, and the included Dockerfile starts:

```text
uvicorn backend.app.main:app --host 0.0.0.0 --port 7860
```

### 1. Create a Space

Create a new Hugging Face Space and choose **Docker** as the SDK. A basic CPU Space is sufficient for the current MiniLM semantic-similarity model for demonstration workloads.

### 2. Push this repository to the Space

From your local SkillSyncer clone, add the Hugging Face Space as a Git remote and push your `main` branch to it. The root YAML metadata, Dockerfile, and port configuration are already included in this repository.

### 3. Add the Gemini secret

In the Hugging Face Space:

`Settings -> Variables and secrets -> New secret`

Create:

```text
GEMINI_API_KEY=<your Gemini API key>
```

Do not commit the real key to GitHub or Hugging Face files.

Optional variable:

```text
GEMINI_MODEL=gemini-3.7-flash
```

The application returns deterministic fallback suggestions if the Gemini key/service is unavailable, so the core scoring API can still run.

### 4. Verify the deployment

After the Docker build succeeds, verify:

```text
https://<your-space-subdomain>.hf.space/health
```

Expected response:

```json
{"status":"ok"}
```

Then open:

```text
https://<your-space-subdomain>.hf.space/docs
```

and test `POST /evaluate/` directly from Swagger UI.

## Database Behavior on Hugging Face

The Docker image writes SQLite runtime data to:

```text
/data/evaluations.db
```

Hugging Face Space disk is ephemeral unless durable storage is attached, so evaluation history can be reset when the Space restarts. For production-style persistence, mount durable storage at `/data` or configure an external database through `DATABASE_URL`.

The backend also supports:

```text
SKILLSYNCER_DB_PATH=/custom/path/evaluations.db
DATABASE_URL=<SQLAlchemy database URL>
```

## Environment Variables

| Variable | Required | Purpose |
|---|---:|---|
| `GEMINI_API_KEY` | For AI suggestions | Gemini API credential |
| `GEMINI_MODEL` | No | Gemini model override; defaults to `gemini-3.7-flash` |
| `SKILLSYNCER_DB_PATH` | No | SQLite file path |
| `DATABASE_URL` | No | Full SQLAlchemy database URL; overrides SQLite path |
| `CORS_ORIGINS` | No | Comma-separated allowed origins; defaults to `*` |
| `SKILLSYNCER_API_URL` | Frontend only | Backend base URL used by Streamlit |

## Important Deployment Fixes Included

This repository now addresses several issues that commonly caused the original Hugging Face deployment to fail:

- FastAPI is served through a Docker Space on port `7860`.
- The container runs as Hugging Face-compatible user ID `1000`.
- `python-dotenv` is explicitly installed.
- Backend imports no longer depend on the current working directory.
- SQLite tables are created automatically at application startup.
- Runtime database location is configurable and container-safe.
- The Hugging Face image installs only backend runtime dependencies.
- The MiniLM model is cached during the Docker build.
- Gemini initialization is lazy instead of crashing application startup when a key is absent.
- The retired `gemini-2.0-flash` model was replaced with a configurable current model.
- Frontend history/detail requests now use the correct `/evaluate/...` routes.
- Frontend backend URL is configurable through an environment variable.

## Responsible Use

Resume-relevance scores are decision-support signals, not autonomous hiring decisions. Human review remains necessary because incomplete resumes, unusual career paths, parsing errors, and biased job descriptions can affect automated matching.

## Author

Maintained by [@rkmaurya93049](https://github.com/rkmaurya93049).
