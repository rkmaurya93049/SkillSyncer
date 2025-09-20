import os
import google.generativeai as genai
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import re


load_dotenv()  

api_key = os.getenv("GEMINI_API_KEY")  

model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", 
    temperature=0.1,
    max_output_tokens=1000,
    google_api_key=api_key     
)



def parse_suggestion(text: str, max_per_section: int = 5) -> dict:
    def extract_section(header: str) -> list:
        match = re.search(f"{header}.*?:\\s*(.*?)\\n\\n", text, re.DOTALL | re.IGNORECASE)
        if match:
            bullets = re.findall(r"\*+\s+(.*)", match.group(1))
            cleaned = [re.sub(r"\*\*|__|\*", "", b).strip() for b in bullets]
            return cleaned[:max_per_section]
        return []

    return {
        "resume_fixes": extract_section("Resume Fixes"),
        "skills_to_add": extract_section("Skills to Add"),
        "experience_suggestions": extract_section("Experience Suggestions")
    }

def generate_suggestions(missing_skills: list, role: str, score: float = None) -> dict:
    prompt = f"""
    The candidate is applying for a role as {role}.
    Their resume received a relevance score of {score}/100.
    The following must-have skills were missing: {', '.join(missing_skills) if missing_skills else 'None explicitly detected'}.
    Please suggest how they can improve their resume or gain relevant experience to better match the job description.
    Format your response in 3 sections:
    1. Resume Fixes (bullet points)
    2. Skills to Add (bullet points)
    3. Experience Suggestions (bullet points)
    """

    try:
        response = model.invoke(prompt)
        return parse_suggestion(response.content)
    except Exception as e:
        return {
            "error": str(e),
            "resume_fixes": [],
            "skills_to_add": [],
            "experience_suggestions": []
        }