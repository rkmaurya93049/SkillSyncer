from langchain.tools import tool
from ..services.parsing import extract_text
from ..services.jd_structuring import jd_structuring
from ..services.resume_matching import compute_hard_match
from ..services.scoring import compute_semantic_similarity, compute_score
from ..services.suggestions import generate_suggestions

@tool
def evaluate_resume(jd_text: str, resume_text: str) -> dict:
    """
    Evaluates a resume against a job description and returns score, verdict, and suggestions.
    """
    jd_result = extract_text("jd.docx", jd_text.encode())
    resume_result = extract_text("resume.pdf", resume_text.encode())

    jd_struct = jd_structuring(jd_result["raw_text"], jd_result["sections"])
    hard_features = compute_hard_match(jd_struct, resume_result["sections"])
    hard_features["semantic_similarity"] = compute_semantic_similarity(jd_result["raw_text"], resume_result["sections"])
    score_result = compute_score(hard_features)
    suggestions = generate_suggestions(hard_features["missing_must_have"], jd_struct["title"])

    return {
        "score": score_result["final_score"],
        "verdict": score_result["verdict"],
        "suggestions": suggestions,
        "missing_must_have": hard_features["missing_must_have"],
        "semantic_similarity": hard_features["semantic_similarity"]
    }