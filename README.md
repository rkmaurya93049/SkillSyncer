# SkillSyncer / RelevAI — Resume Relevance Checker

A full-stack resume-evaluation project that compares resumes with job requirements and provides relevance scoring and improvement feedback for candidate and recruiter workflows.

## Overview

The repository combines a **FastAPI backend** with a **Streamlit frontend**. The project is designed around resume parsing, job-description alignment, semantic matching and feedback generation.

## Core Capabilities

- Student-oriented resume evaluation workflow
- Recruiter-oriented candidate/job-description comparison
- Resume parsing for common document formats
- Skill and text matching
- Semantic similarity / embedding-based alignment
- Scoring and feedback workflow
- Database-backed result/history support in the application design
- LLM-oriented integration experiments for suggestions

## Repository Structure

```text
SkillSyncer/
├── backend/
│   └── app/               # FastAPI/backend application code
├── frontend/
│   ├── components/        # Streamlit UI components
│   ├── dashboard.py       # Frontend entry point
│   └── requirements.txt
├── .devcontainer/         # Development-container configuration
├── .gitignore
└── README.md
```

## Technologies Used

The project includes or experiments with technologies such as:

- Python
- FastAPI + Uvicorn
- Streamlit
- Pydantic / SQLAlchemy
- PDF/DOCX parsing libraries
- spaCy and RapidFuzz
- sentence-transformers / scikit-learn
- LangChain / LangGraph
- ChromaDB
- Google Generative AI integration

Exact dependencies should be taken from the requirement files and application code in the relevant component.

## Local Setup

### Backend

From the repository root, enter the backend environment and install its required dependencies according to the backend configuration, then run the FastAPI application. The intended application module is under `backend/app/`.

A typical development command is:

```bash
uvicorn app.main:app --reload
```

Run it from the directory/environment where the `app` package and backend dependencies are available.

### Frontend

```bash
cd frontend
pip install -r requirements.txt
streamlit run dashboard.py
```

## Environment Variables

Some AI-assisted features may require provider credentials. Keep keys in local environment variables or a `.env` file; never commit real credentials.

Example:

```text
GEMINI_API_KEY=your_key_here
```

The repository `.gitignore` excludes local environment files and Python cache artifacts.

## Responsible Use

Resume relevance scores should be treated as decision-support signals, not as an autonomous hiring decision. Human review is necessary, especially where incomplete resumes, unusual career paths or biased job descriptions could affect automated matching.

## Development Notes

- Generated Python bytecode/cache files are intentionally excluded from version control.
- Keep model/provider credentials outside Git.
- Add automated tests and a documented backend requirements file if the application is prepared for deployment.

## Author

Maintained by [@rkmaurya93049](https://github.com/rkmaurya93049).
