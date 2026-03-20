# ats/nlp_features.py
import re
from typing import Dict, List, Optional
import spacy
from pathlib import Path
import json

nlp = spacy.load("en_core_web_sm")

EMAIL_RE = re.compile(r"[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+")
PHONE_RE = re.compile(r"(?:(?:\+?\d{1,3}[\s-])?(?:\(?\d{2,4}\)?[\s-]?)?\d{3,4}[\s-]?\d{3,4})")
SECTION_HEADERS = ["education", "experience", "projects", "skills", "summary", "certifications", "achievements", "profile", "work experience"]

SEED_SKILLS = {
    "python", "java", "c++", "c", "javascript", "react", "node", "aws",
    "docker", "kubernetes", "sql", "postgresql", "mongodb", "nlp", "tensorflow",
    "pytorch", "scikit-learn", "git", "linux", "bash", "rest", "graphql"
}

TIERS_PATH = Path("institution_tiers.json")
if TIERS_PATH.exists():
    _INSTITUTION_TIERS = {k.lower(): float(v) for k, v in json.loads(TIERS_PATH.read_text(encoding="utf-8")).items()}
else:
    _INSTITUTION_TIERS = {}

def extract_contacts(text: str) -> Dict[str, List[str]]:
    emails = list(dict.fromkeys(EMAIL_RE.findall(text)))
    phones = list(dict.fromkeys(PHONE_RE.findall(text)))
    return {"emails": emails, "phones": phones}

def extract_name(text: str) -> str:
    doc = nlp(text[:1500])
    persons = [ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"]
    return persons[0] if persons else ""

def split_sections(text: str) -> Dict[str, List[str]]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    sections = {}
    current = "header"
    sections[current] = []
    for ln in lines:
        low = ln.lower()
        header_found = None
        for h in SECTION_HEADERS:
            if low.startswith(h) or (h in low and len(ln.split()) <= 4):
                header_found = h
                break
        if header_found:
            current = header_found
            sections.setdefault(current, [])
            if len(ln.split()) > 1:
                sections[current].append(ln)
        else:
            sections.setdefault(current, []).append(ln)
    return sections

def normalize_name(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def extract_institution_from_education(education_lines: List[str]) -> Optional[str]:
    if not education_lines:
        return None
    for ln in education_lines:
        ln_norm = normalize_name(ln)
        if any(k in ln_norm for k in ["iit", "nit", "institute", "college", "university", "school"]):
            return ln_norm
    return normalize_name(education_lines[0]) if education_lines else None

def get_institution_score(name: Optional[str]) -> float:
    if not name:
        return 0.0
    name = normalize_name(name)
    for key, val in _INSTITUTION_TIERS.items():
        if key in name or name in key:
            return float(val)
    return 0.5

def extract_skills(text: str, seed_skills=None) -> List[str]:
    s = set(skill.lower() for skill in (seed_skills or SEED_SKILLS))
    found = set()
    tokens = re.split(r"[,\n;/()]+", text.lower())
    for t in tokens:
        t = t.strip()
        if not t: continue
        for skill in s:
            if skill in t:
                found.add(skill)
    return sorted(found)

def extract_education_fields(education_lines: List[str]) -> Dict:
    inst = extract_institution_from_education(education_lines)
    return {"institution": inst, "raw": education_lines}

def extract_experience_fields(exp_lines: List[str]) -> Dict:
    exp_text = "\n".join(exp_lines)
    skills = extract_skills(exp_text)
    years = re.findall(r"\b(\d{4})\b", exp_text)
    return {"raw": exp_lines, "skills": skills, "years_tokens": years}

def extract_all(text: str) -> Dict:
    sections = split_sections(text)
    name = extract_name(text)
    contacts = extract_contacts(text)
    skills = extract_skills("\n".join(sections.get("skills", []) + sections.get("header", [])))
    education = extract_education_fields(sections.get("education", []))
    experience = extract_experience_fields(sections.get("experience", []))
    projects = sections.get("projects", [])
    summary = "\n".join(sections.get("summary", [])[:5]) if sections.get("summary") else ""
    inst_score = get_institution_score(education.get("institution"))
    return {
        "name": name,
        "contacts": contacts,
        "skills": skills,
        "education": education,
        "experience": experience,
        "projects": projects,
        "summary": summary,
        "institution_score": inst_score,
        "raw_sections": sections
    }
