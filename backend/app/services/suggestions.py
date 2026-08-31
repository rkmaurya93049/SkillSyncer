import os
import re
from functools import lru_cache

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

DEFAULT_GEMINI_MODEL = "gemini-3.7-flash"


@lru_cache(maxsize=1)
def get_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    return ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL),
        temperature=0.1,
        max_output_tokens=1000,
        google_api_key=api_key,
    )


def parse_suggestion(text: str, max_per_section: int = 5) -> dict:
    def extract_section(header: str) -> list:
        pattern = rf"{re.escape(header)}.*?:\s*(.*?)(?:\n\n|\Z)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if not match:
            return []

        bullets = re.findall(r"(?:^|\n)\s*(?:[-*•]|\d+\.)\s+(.*)", match.group(1))
        cleaned = [re.sub(r"\*\*|__|\*", "", bullet).strip() for bullet in bullets]
        return [item for item in cleaned if item][:max_per_section]

    return {
        "resume_fixes": extract_section("Resume Fixes"),
        "skills_to_add": extract_section("Skills to Add"),
        "experience_suggestions": extract_section("Experience Suggestions"),
    }


def _fallback_suggestions(missing_skills: list, role: str, error: str | None = None) -> dict:
    skills = [str(skill).strip() for skill in missing_skills if str(skill).strip()][:5]
    return {
        "error": error,
        "resume_fixes": [
            f"Tailor the summary and project bullets to the {role} requirements.",
            "Use measurable outcomes and concrete technologies in experience/project bullets.",
        ],
        "skills_to_add": skills,
        "experience_suggestions": [
            "Add a focused project or practical example demonstrating the highest-priority missing skills."
        ],
    }


def generate_suggestions(missing_skills: list, role: str, score: float | None = None) -> dict:
    model = get_model()
    if model is None:
        return _fallback_suggestions(
            missing_skills,
            role,
            error="GEMINI_API_KEY is not configured; deterministic fallback suggestions were returned.",
        )

    prompt = f"""
The candidate is applying for a role as {role}.
Their resume received a relevance score of {score}/100.
The following must-have skills were missing: {', '.join(missing_skills) if missing_skills else 'None explicitly detected'}.

Suggest concise, practical improvements. Format the response using exactly these sections:

Resume Fixes:
- bullet points

Skills to Add:
- bullet points

Experience Suggestions:
- bullet points
"""

    try:
        response = model.invoke(prompt)
        parsed = parse_suggestion(response.content)
        if not any(parsed.values()):
            return _fallback_suggestions(missing_skills, role, error="Gemini returned an unparseable response.")
        parsed["error"] = None
        return parsed
    except Exception as exc:
        return _fallback_suggestions(missing_skills, role, error=str(exc))
