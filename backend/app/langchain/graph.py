from typing import TypedDict

from langgraph.graph import END, StateGraph

from ..services.jd_structuring import jd_structuring
from ..services.parsing import extract_text
from ..services.resume_matching import compute_hard_match
from ..services.scoring import compute_score, compute_semantic_similarity
from ..services.suggestions import generate_suggestions


class ResumeState(TypedDict):
    jd_text: str
    resume_text: str
    jd_struct: dict
    resume_sections: dict
    features: dict
    score: dict
    suggestions: dict


def parse_jd(state: ResumeState) -> ResumeState:
    jd_result = extract_text("jd.txt", state["jd_text"].encode("utf-8"))
    jd_struct = jd_structuring(jd_result["raw_text"], jd_result["sections"])
    return {**state, "jd_struct": jd_struct}


def parse_resume(state: ResumeState) -> ResumeState:
    resume_result = extract_text("resume.txt", state["resume_text"].encode("utf-8"))
    return {**state, "resume_sections": resume_result["sections"]}


def match_and_score(state: ResumeState) -> ResumeState:
    features = compute_hard_match(state["jd_struct"], state["resume_sections"])
    features["semantic_similarity"] = compute_semantic_similarity(
        state["jd_text"],
        state["resume_sections"],
    )
    score = compute_score(features)
    return {**state, "features": features, "score": score}


def suggest_improvements(state: ResumeState) -> ResumeState:
    suggestions = generate_suggestions(
        missing_skills=state["features"]["missing_must_have"],
        role=state["jd_struct"]["title"],
        score=state["score"]["final_score"],
    )
    return {**state, "suggestions": suggestions}


graph = StateGraph(ResumeState)
graph.add_node("parse_jd", parse_jd)
graph.add_node("parse_resume", parse_resume)
graph.add_node("match_and_score", match_and_score)
graph.add_node("suggest", suggest_improvements)

graph.set_entry_point("parse_jd")
graph.add_edge("parse_jd", "parse_resume")
graph.add_edge("parse_resume", "match_and_score")
graph.add_edge("match_and_score", "suggest")
graph.add_edge("suggest", END)

resume_graph = graph.compile()
