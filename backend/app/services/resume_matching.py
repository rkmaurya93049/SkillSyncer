from typing import List, Dict, Tuple
from rapidfuzz import fuzz

def extract_skills_from_resume(sections: Dict[str, str]) -> List[str]:
    skill_keys = ["skills", "technical_skills", "projects", "experience"]
    skills = []
    for key in skill_keys:
        if key in sections:
            lines = sections[key].splitlines()
            for line in lines:
                line = line.strip("•-•* \t").lower()
                if len(line) > 1 and not line.startswith("location"):
                    skills.append(line)
    return list(set(skills))

def match_skills(jd_skills: List[str], resume_skills: List[str], threshold: int = 80) -> Tuple[int, List[str]]:
    matched = []
    for jd_skill in jd_skills:
        for res_skill in resume_skills:
            score = fuzz.partial_ratio(jd_skill.lower(), res_skill.lower())
            if score >= threshold:
                matched.append(jd_skill)
                break
    return len(matched), [s for s in jd_skills if s not in matched]

def compute_hard_match(jd: Dict, resume_sections: Dict) -> Dict:
    resume_skills = extract_skills_from_resume(resume_sections)

    must_have = jd.get("must_have", [])
    nice_to_have = jd.get("nice_to_have", [])
    degrees_required = jd.get("degrees", [])
    years_required = jd.get("years_required", 0)

    must_matched, must_missing = match_skills(must_have, resume_skills)
    nice_matched, nice_missing = match_skills(nice_to_have, resume_skills)

    must_score = round(must_matched / max(len(must_have), 1), 2)
    nice_score = round(nice_matched / max(len(nice_to_have), 1), 2)

    # Degree match
    resume_text = " ".join(resume_sections.values()).lower()
    degree_match = any(deg in resume_text for deg in degrees_required)

    # Experience match (stubbed for now)
    experience_match = 1.0 if years_required == 0 else 0.5  # We'll refine this later

    return {
        "must_have_score": must_score,
        "nice_to_have_score": nice_score,
        "degree_match": degree_match,
        "experience_match": experience_match,
        "missing_must_have": must_missing,
        "missing_nice_to_have": nice_missing
    }

