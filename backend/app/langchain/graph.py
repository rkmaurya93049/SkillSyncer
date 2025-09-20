import os
from langgraph.graph import StateGraph, END
from typing import TypedDict
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.app.services.parsing import extract_text
from backend.app.services.jd_structuring import jd_structuring
from backend.app.services.resume_matching import compute_hard_match
from backend.app.services.scoring import compute_semantic_similarity, compute_score
from backend.app.services.suggestions import generate_suggestions
# Configure Gemini
load_dotenv()  # Load variables from your .env file

api_key = os.getenv("GEMINI_API_KEY")  # Safely access your key

model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",  # ✅ Make sure this model is available
    temperature=0.1,
    max_output_tokens=1000,
    google_api_key=api_key     # ✅ This is what tells LangChain to use your key
)


# Define state schema
class ResumeState(TypedDict):
    jd_text: str
    resume_text: str
    jd_struct: dict
    resume_sections: dict
    features: dict
    score: dict
    suggestions: str

# Node 1: Parse JD
def parse_jd(state: ResumeState) -> ResumeState:
    jd_result = extract_text("jd.docx", state["jd_text"])
    jd_struct = jd_structuring(jd_result["raw_text"], jd_result["sections"])
    return {**state, "jd_struct": jd_struct}

# Node 2: Parse Resume
def parse_resume(state: ResumeState) -> ResumeState:
    resume_result = extract_text("resume.pdf", state["resume_text"])
    return {**state, "resume_sections": resume_result["sections"]}

# Node 3: Match & Score
def match_and_score(state: ResumeState) -> ResumeState:
    features = compute_hard_match(state["jd_struct"], state["resume_sections"])
    features["semantic_similarity"] = compute_semantic_similarity(state["jd_text"], state["resume_sections"])
    score = compute_score(features)
    return {**state, "features": features, "score": score}

def suggest_improvements(state: ResumeState) -> ResumeState:
    suggestions = generate_suggestions(
        missing_skills=state["features"]["missing_must_have"],
        role=state["jd_struct"]["title"],
        score=state["score"]["final_score"]  # ✅ Pass the score here
    )
    return {**state, "suggestions": suggestions}

# Build LangGraph
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