from fastapi import APIRouter, UploadFile, File, HTTPException
from services.parsing import extract_text
from services.jd_structuring import jd_structuring

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/jd")
async def upload_jd(file: UploadFile = File(...)):
    content = await file.read()
    result = extract_text(file.filename, content)
    if not result.get("raw_text"):
        raise HTTPException(status_code=400, detail="Unable to extract text from file.")

    structured = jd_structuring(result["raw_text"], result["sections"])

    return {
        "filename": file.filename,
        "title": structured["title"],
        "must_have_skills": structured["must_have"],
        "nice_to_have_skills": structured["nice_to_have"],
        "years_required": structured["years_required"],
        "degrees": structured["degrees"],
        "chars": len(result["raw_text"]),
        "sample": result["raw_text"][:600]

    }
