# 🚀 RelevAI — Resume Relevance Checker

📌 Project Overview
The Resume Evaluator is a full‑stack application that helps both students and recruiters (HR) by analyzing resumes against specific job roles. It provides a score based on skill matching, experience, and job description alignment, along with actionable suggestions for improvement.
The system is designed to streamline the hiring process for recruiters and guide students in tailoring their resumes for better opportunities.

🚀 Features
- Dual Views:
- 🎓 Student View – Upload resume, select job role, and receive feedback + improvement suggestions
- 🧑‍💼 Recruiter View – Evaluate resumes against job descriptions with scoring and insights
- Scoring Engine: Skill matching, experience relevance, and JD alignment
- Suggestions: Personalized recommendations for both HR and students
- Database Integration: Resume history stored in SQL for future analysis and reporting
- Fast & Interactive UI: Built with Streamlit for a smooth user experience

🛠️ Tech Stack & Libraries
Frontend
- Streamlit – interactive dashboards for students & recruiters
Backend
- FastAPI (fastapi==0.111.0) – REST API for resume parsing, scoring, and suggestions
- Uvicorn (uvicorn[standard]==0.30.1) – ASGI server
- Python‑Multipart (python-multipart==0.0.9) – file upload handling
Resume Parsing & Processing
- pdfplumber (0.11.4) – extract text from PDF resumes
- PyMuPDF (pymupdf==1.24.9) – advanced PDF parsing
- docx2txt – extract text from DOCX resumes
NLP & Machine Learning
- spaCy (3.7.5) – NLP pipeline for text preprocessing
- rapidfuzz (3.9.6) – fuzzy string matching for skills
- sentence-transformers (3.0.1) – semantic embeddings for JD‑resume alignment
- scikit-learn (1.5.1) – preprocessing, scoring logic, evaluation
- numpy (1.26.4) – numerical computations
Database & ORM
- SQLAlchemy (2.0.32) – ORM for SQL database integration
- Pydantic (2.8.2) – data validation and schema management
AI/LLM Integrations
- LangChain – orchestration of LLM workflows
- LangGraph – graph‑based reasoning for evaluation pipelines
- ChromaDB – vector database for embeddings storage
- langchain-google-genai – integration with Google Generative AI
- google-generativeai – LLM‑powered suggestions

📈 Workflow
- Student uploads resume + selects job role
- FastAPI backend parses resume and compares it with job description
- Scoring engine evaluates skills, experience, and JD alignment
- Suggestions generated for both students (resume improvement) and HR (candidate fit)
- Results stored in SQL database for future analysis

👤 Contributor
- Raushan Kumar – Full‑stack ML Developer & AI Workflow Architect
- Implemented Streamlit frontend, FastAPI backend, resume parsing pipeline, scoring engine, SQL database integration, and LLM‑powered suggestions


## 🛠️ Installation
-**env**:add .env file before running this which contain GEMNINI_API_KEY

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

cd frontend
pip install -r requirements.txt
streamlit run dashboard.py
