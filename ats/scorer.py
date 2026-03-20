# ats/scorer.py
import numpy as np
from numpy.linalg import norm
from typing import Dict, List
from .embeddings import embed_text

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    denom = (norm(a) * norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)

def keyword_score(resume_skills: List[str], jd_skills: List[str]) -> float:
    if not jd_skills:
        return 0.0
    matched = set([s.lower() for s in resume_skills]).intersection(set([s.lower() for s in jd_skills]))
    return len(matched) / max(1, len(jd_skills))

def semantic_score(resume_text: str, jd_text: str) -> float:
    r_vec = embed_text(resume_text)
    jd_vec = embed_text(jd_text)
    return cosine_sim(r_vec, jd_vec)

def compute_hsk_score(parsed_resume: Dict, jd_text: str, jd_skills: List[str],
                      weights: Dict = None, inst_weight: float = 0.05) -> Dict:
    if weights is None:
        weights = {"semantic": 0.55, "keyword": 0.35, "heuristic": 0.10}

    resume_skills = parsed_resume.get("skills", [])
    sem = semantic_score(parsed_resume.get("summary", "") + " " + " ".join(resume_skills), jd_text)
    kw = keyword_score(resume_skills, jd_skills)

    heuristic_base = 0.0
    if parsed_resume.get("education") and parsed_resume["education"].get("raw"):
        heuristic_base += 0.05
    if parsed_resume.get("experience") and parsed_resume["experience"].get("raw"):
        heuristic_base += 0.03

    inst_score = float(parsed_resume.get("institution_score", 0.5))
    inst_contrib = inst_score * inst_weight

    heuristic_total = heuristic_base + inst_contrib

    combined = weights["semantic"] * sem + weights["keyword"] * kw + weights["heuristic"] * heuristic_total
    final = float(max(0.0, min(1.0, combined)) * 100.0)

    return {
        "final_score": round(final, 2),
        "semantic_pct": round(sem * 100, 2),
        "keyword_pct": round(kw * 100, 2),
        "heuristic_pct": round(heuristic_total * 100, 2),
        "institution_score_pct": round(inst_score * 100, 2)
    }
