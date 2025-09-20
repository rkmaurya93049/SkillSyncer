from fastapi import APIRouter, UploadFile
from backend.app.langchain.graph import resume_graph

router = APIRouter()

@router.post("/evaluate-graph")
async def evaluate_graph(jd: UploadFile, resume: UploadFile):
    jd_bytes = await jd.read()
    resume_bytes = await resume.read()

    result = resume_graph.invoke({
        "jd_text": jd_bytes,
        "resume_text": resume_bytes
    })

    return {
        "score": result["score"]["final_score"],
        "verdict": result["score"]["verdict"],
        "suggestions": result["suggestions"]
    }