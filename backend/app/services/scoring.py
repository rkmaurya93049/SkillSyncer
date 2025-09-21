from typing import Dict
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load once
model = SentenceTransformer("all-MiniLM-L6-v2")

def compute_semantic_similarity(jd_text: str, resume_sections: Dict[str, str]) -> float:
    # Compare JD to resume summary + experience
    resume_text = ""
    for key in ["summary", "experience", "projects"]:
        if key in resume_sections:
            resume_text += resume_sections[key] + "\n"

    if not resume_text.strip():
        return 0.0

    jd_emb = model.encode([jd_text], convert_to_tensor=True)
    res_emb = model.encode([resume_text], convert_to_tensor=True)

    sim = cosine_similarity(jd_emb.cpu().numpy(), res_emb.cpu().numpy())[0][0]
    return round(float(sim), 3)

def compute_score(features: Dict, weights: Dict = None) -> Dict:
    # Default weights
    w = weights or {
        "must_have": 40,
        "nice_to_have": 10,
        "degree": 5,
        "experience": 10,
        "semantic": 35
    }

    score = (
        w["must_have"] * features["must_have_score"] +
        w["nice_to_have"] * features["nice_to_have_score"] +
        w["degree"] * (1.0 if features["degree_match"] else 0.0) +
        w["experience"] * features["experience_match"] +
        w["semantic"] * features["semantic_similarity"]
    )

    final_score = round(score / sum(w.values()) * 100, 1)

    if final_score >= 75:
        verdict = "High"
    elif final_score >= 50:
        verdict = "Medium"
    else:
        verdict = "Low"

    return {
        "final_score": final_score,
        "verdict": verdict
    }


