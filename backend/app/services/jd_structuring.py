import re
from typing import Dict, List

DEGREE_KEYWORDS = ["bachelor", "master", "b.tech", "btech", "m.tech", "mtech", "be", "me", "bsc", "msc", "mca"]
YEARS_PAT = re.compile(r"(\d+)\+?\s+(years?|yrs?)", re.I)

def split_bullets(text: str) -> List[str]:
    items = re.split(r"\n[-•*]\s+|\r\n[-•*]\s+|\n\d+\.\s+", text)
    items = [it.strip(" -•*.\t") for it in items if it and len(it.strip()) > 1]
    return items

def extract_title(raw_text: str) -> str:
    # Simple: first line with role-like words
    for line in raw_text.splitlines()[:10]:
        if any(k in line.lower() for k in ["engineer", "developer", "analyst", "scientist", "manager", "designer"]):
            return line.strip()[:120]
    return raw_text.splitlines()[0].strip()[:120] if raw_text else "Role"

def jd_structuring(raw_text: str, sections: Dict[str, str]) -> Dict:
    text_low = raw_text.lower()

    must_have, nice_to_have = [], []

    # Heuristics: look for specific headers in JD
    for key, val in sections.items():
        kl = key.lower()
        if "requirement" in kl or "must" in kl or "responsibilit" in kl:
            must_have.extend(split_bullets(val))
        if "good" in kl or "preferred" in kl or "nice" in kl:
            nice_to_have.extend(split_bullets(val))
        if "qualification" in kl or "education" in kl:
            nice_to_have.extend(split_bullets(val))

    # Fallback: if empty, mine lines containing "experience", "proficient", "knowledge of"
    if not must_have:
        must_have = [ln.strip() for ln in raw_text.splitlines() if any(
            kw in ln.lower() for kw in ["experience", "proficient", "hands-on", "required", "responsibilities"]
        )][:12]

    # Years of experience
    yrs = YEARS_PAT.findall(raw_text)
    years_required = max([int(y[0]) for y in yrs], default=0)

    # Degrees
    degrees = [d for d in DEGREE_KEYWORDS if d in text_low]

    return {
        "title": extract_title(raw_text),
        "must_have": must_have[:20],
        "nice_to_have": nice_to_have[:20],
        "years_required": years_required,
        "degrees": degrees
    }