# pages/2_Upload.py
import streamlit as st
from pathlib import Path
import tempfile
import os
import json
from ats.parser import extract_text
from ats.nlp_features import extract_all
from ats.scorer import compute_hsk_score
from ats.db import init_db, ResumeRecord
from ats.gemini_client import explain_with_gemini

def process_uploaded_file(uploaded_file):
    suffix = Path(uploaded_file.name).suffix.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        return tmp.name

st.title("Upload Resumes & Job Description")
st.markdown("Upload one or more resumes and a job description. Enter JD skills (comma separated).")

use_gemini_default = bool(os.getenv("GEMINI_API_KEY"))
use_gemini = st.sidebar.checkbox("Use Gemini", value=use_gemini_default)
if st.sidebar.text_input("Paste Gemini API key (optional)", type="password"):
    # streamlit will set env var if user pastes; handled externally in main flow if you wire it.
    pass

jd_file = st.file_uploader("Upload JD (.txt) optional", type=["txt"])
jd_text_area = st.text_area("Or paste JD text here", height=150)
skills_input = st.text_input("JD skills (comma separated)", value="python, nlp, docker")

if jd_file:
    jd_temp = process_uploaded_file(jd_file)
    with open(jd_temp, "r", encoding="utf-8", errors="ignore") as f:
        jd_text = f.read()
elif jd_text_area.strip():
    jd_text = jd_text_area
else:
    jd_text = ""

uploaded = st.file_uploader("Upload one or more resumes (pdf/docx/txt)", accept_multiple_files=True, type=["pdf","docx","txt"])

if st.button("Run ATS"):
    if not jd_text:
        st.error("Please provide job description text or file.")
    elif not uploaded:
        st.error("Please upload resumes.")
    else:
        js = [s.strip() for s in skills_input.split(",") if s.strip()]
        Session = init_db("sqlite:///ats_results.db")
        session = Session()
        results = []
        progress = st.progress(0)
        for i, up in enumerate(uploaded):
            tmp = process_uploaded_file(up)
            text = extract_text(tmp)
            parsed = extract_all(text)
            score = compute_hsk_score(parsed, jd_text, js)
            gemini_text = ""
            if use_gemini:
                gemini_text = explain_with_gemini(text, jd_text, score)
            rec = ResumeRecord(
                filename=up.name,
                resume_text=text,
                parsed_json=json.dumps(parsed),
                jd_text=jd_text,
                score_json=json.dumps(score),
                gemini_explain=gemini_text
            )
            session.add(rec)
            session.commit()
            results.append({"file": up.name, "parsed": parsed, "score": score, "gemini": gemini_text})
            progress.progress((i+1)/len(uploaded))
        st.success("Processing done. Go to Results page.")
        st.session_state["results"] = results
