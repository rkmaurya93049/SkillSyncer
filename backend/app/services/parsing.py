import io
import re
from typing import Dict, Optional
import pdfplumber
import fitz  
import docx2txt

SECTION_HEADERS = [
    "summary", "objective", "skills", "technical skills", "experience",
    "work experience", "professional experience", "projects", "education",
    "certifications", "achievements", "publications"
]

def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    return text

def extract_text_pdfplumber(file_bytes: bytes) -> Optional[str]:
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = [page.extract_text(x_tolerance=1, y_tolerance=1) or "" for page in pdf.pages]
        text = "\n".join(pages)
        return clean_text(text)
    except Exception:
        return None

def extract_text_pymupdf(file_bytes: bytes) -> Optional[str]:
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        blocks = []
        for page in doc:
            blocks.append(page.get_text("text"))
        text = "\n".join(blocks)
        return clean_text(text)
    except Exception:
        return None

def extract_text_docx(file_bytes: bytes) -> Optional[str]:
    try:
        text = docx2txt.process(io.BytesIO(file_bytes))
        return clean_text(text or "")
    except Exception:
        return None

def detect_filetype(filename: str) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        return "pdf"
    if name.endswith(".docx"):
        return "docx"
    return "txt"

def heuristic_section_split(text: str) -> Dict[str, str]:
    lines = [ln.strip() for ln in text.splitlines()]
    indices = []
    for i, ln in enumerate(lines):
        ln_low = ln.lower().strip(":")
        if ln_low in SECTION_HEADERS or any(
            ln_low.startswith(h) for h in SECTION_HEADERS
        ):
            indices.append((i, ln_low))
    # Append end sentinel
    indices.append((len(lines), "END"))

    sections = {}
    for idx in range(len(indices) - 1):
        start_i, header = indices[idx]
        end_i, _ = indices[idx + 1]
        content = "\n".join(lines[start_i + 1:end_i]).strip()
        header_key = header.replace(" ", "_")
        if content:
            sections[header_key] = content
    # Fallbacks
    if "skills" not in sections and "technical_skills" in sections:
        sections["skills"] = sections["technical_skills"]
    return sections

def extract_text(filename: str, file_bytes: bytes) -> Dict:
    ftype = detect_filetype(filename)
    text = ""
    if ftype == "pdf":
        text = extract_text_pdfplumber(file_bytes) or ""
        if len(text) < 50:
            text = extract_text_pymupdf(file_bytes) or ""
    elif ftype == "docx":
        text = extract_text_docx(file_bytes) or ""
    else:
        # raw bytes as utf-8 if plain text
        try:
            text = file_bytes.decode("utf-8", errors="ignore")
        except Exception:
            text = ""
    text = clean_text(text or "")
    sections = heuristic_section_split(text) if text else {}
    return {
        "filetype": ftype,
        "raw_text": text,
        "sections": sections
    }