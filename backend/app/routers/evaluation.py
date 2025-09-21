from fastapi import APIRouter, UploadFile, File, HTTPException
from services.parsing import extract_text
from services.jd_structuring import jd_structuring
from services.resume_matching import compute_hard_match
from services.scoring import compute_semantic_similarity, compute_score
from services.suggestions import generate_suggestions
from fastapi import Depends
from sqlalchemy.orm import Session
from session import SessionLocal
from models.evaluation import ResumeEvaluation
from fastapi import Query
from datetime import datetime
import csv
from fastapi.responses import JSONResponse, StreamingResponse
from io import StringIO


router = APIRouter(prefix="/evaluate", tags=["evaluation"])

@router.post("/")
async def evaluate(jd_file: UploadFile = File(...), resume_file: UploadFile = File(...)):
    # Step 1: Read files
    jd_bytes = await jd_file.read()
    resume_bytes = await resume_file.read()

    # Step 2: Extract text
    jd_result = extract_text(jd_file.filename, jd_bytes)
    resume_result = extract_text(resume_file.filename, resume_bytes)

    # Step 3: Validate
    if not jd_result.get("raw_text") or not resume_result.get("raw_text"):
        raise HTTPException(status_code=400, detail="Failed to extract text from one or both files.")

    # Step 4: Structure and score
    jd_struct = jd_structuring(jd_result["raw_text"], jd_result["sections"])
    hard_features = compute_hard_match(jd_struct, resume_result["sections"])
    semantic_score = compute_semantic_similarity(jd_result["raw_text"], resume_result["sections"])
    hard_features["semantic_similarity"] = semantic_score
    score_result = compute_score(hard_features)
    suggestions = generate_suggestions(
        missing_skills=hard_features["missing_must_have"],
        role=jd_struct["title"],
        score=score_result["final_score"]
    )

 

    db = SessionLocal()
    record = ResumeEvaluation(
        jd_title=jd_struct["title"],
        resume_filename=resume_file.filename,
        score=score_result["final_score"],
        verdict=score_result["verdict"],
        semantic_similarity=semantic_score,
        must_have_score=hard_features["must_have_score"],
        nice_to_have_score=hard_features["nice_to_have_score"],
        degree_match=str(hard_features["degree_match"]),
        experience_match=hard_features["experience_match"],
        missing_must_have=hard_features["missing_must_have"],
        missing_nice_to_have=hard_features["missing_nice_to_have"],
        suggestions=suggestions
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # Step 6: Return response
    return {
        "jd_title": jd_struct["title"],
        "resume_filename": resume_file.filename,
        "score": score_result["final_score"],
        "verdict": score_result["verdict"],
        "semantic_similarity": semantic_score,
        "must_have_score": hard_features["must_have_score"],
        "nice_to_have_score": hard_features["nice_to_have_score"],
        "degree_match": hard_features["degree_match"],
        "experience_match": hard_features["experience_match"],
        "missing_must_have": hard_features["missing_must_have"],
        "missing_nice_to_have": hard_features["missing_nice_to_have"],
        "suggestions": suggestions
    }

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/history")
def get_history(
    verdict: str = Query(None),
    min_score: float = Query(None),
    max_score: float = Query(None),
    jd_title: str = Query(None),
    resume_filename: str = Query(None),
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(ResumeEvaluation)

    if verdict:
        query = query.filter(ResumeEvaluation.verdict == verdict)
    if min_score is not None:
        query = query.filter(ResumeEvaluation.score >= min_score)
    if max_score is not None:
        query = query.filter(ResumeEvaluation.score <= max_score)
    if jd_title:
        query = query.filter(ResumeEvaluation.jd_title.ilike(f"%{jd_title}%"))
    if resume_filename:
        query = query.filter(ResumeEvaluation.resume_filename.ilike(f"%{resume_filename}%"))
    if start_date:
        query = query.filter(ResumeEvaluation.timestamp >= start_date)
    if end_date:
        query = query.filter(ResumeEvaluation.timestamp <= end_date)

    records = query.order_by(ResumeEvaluation.timestamp.desc()).all()

    return [
        {
            "id": r.id,
            "jd_title": r.jd_title,
            "resume_filename": r.resume_filename,
            "score": r.score,
            "verdict": r.verdict,
            "timestamp": r.timestamp.isoformat()
        }
        for r in records
    ]
@router.get("/export/json")
def export_json(db: Session = Depends(get_db)):
    records = db.query(ResumeEvaluation).order_by(ResumeEvaluation.timestamp.desc()).all()
    return [
        {
            "id": r.id,
            "jd_title": r.jd_title,
            "resume_filename": r.resume_filename,
            "score": r.score,
            "verdict": r.verdict,
            "semantic_similarity": r.semantic_similarity,
            "must_have_score": r.must_have_score,
            "nice_to_have_score": r.nice_to_have_score,
            "degree_match": r.degree_match,
            "experience_match": r.experience_match,
            "missing_must_have": r.missing_must_have,
            "missing_nice_to_have": r.missing_nice_to_have,
            "suggestions": r.suggestions,
            "timestamp": r.timestamp.isoformat()
        }
        for r in records
    ]


@router.get("/export/csv")
def export_csv(db: Session = Depends(get_db)):
    records = db.query(ResumeEvaluation).order_by(ResumeEvaluation.timestamp.desc()).all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "jd_title", "resume_filename", "score", "verdict", "semantic_similarity",
        "must_have_score", "nice_to_have_score", "degree_match", "experience_match", "timestamp"
    ])

    for r in records:
        writer.writerow([
            r.id, r.jd_title, r.resume_filename, r.score, r.verdict, r.semantic_similarity,
            r.must_have_score, r.nice_to_have_score, r.degree_match, r.experience_match, r.timestamp
        ])

    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=evaluations.csv"})


@router.get("/{id}")
def get_evaluation_by_id(id: int, db: Session = Depends(get_db)):
    record = db.query(ResumeEvaluation).filter(ResumeEvaluation.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    return {
    "id": record.id,
    "jd_title": record.jd_title,
    "resume_filename": record.resume_filename,
    "score": record.score,
    "verdict": record.verdict,
    "semantic_similarity": record.semantic_similarity,
    "must_have_score": record.must_have_score,
    "nice_to_have_score": record.nice_to_have_score,
    "degree_match": record.degree_match,
    "experience_match": record.experience_match,
    "missing_skills": record.missing_must_have,
    "feedback": "\n".join(record.suggestions.get("resume_fixes", [])),  # ✅ This line
    "timestamp": record.timestamp.isoformat()

}
