# 🚀 RelevAI — Resume Relevance Checker

## 🧠 Problem Statement
Build an AI-powered system that evaluates resume relevance against job descriptions. The goal is to assist students and recruiters in identifying skill gaps, improving resumes, and filtering candidates efficiently.

## 🎯 Approach
- **Frontend**: Streamlit dashboard with student and recruiter views
- **Backend**: FastAPI service for resume evaluation
- **Scoring**: Based on skill matching, experience, and JD alignment
- **DB**: history saving for the future analysis of the resumes

## 🛠️ Installation

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

cd frontend
pip install -r requirements.txt
streamlit run dashboard.py
