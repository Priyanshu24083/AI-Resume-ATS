# pages/4_Database.py
import streamlit as st
import pandas as pd
from ats.db import init_db
from sqlalchemy import text
import json

st.title("Database Viewer")

Session = init_db("sqlite:///ats_results.db")
session = Session()

# fixed SQL query
query = session.execute(
    text("SELECT id, filename, created_at, score_json FROM resumes ORDER BY created_at DESC LIMIT 50")
)

rows = []
for r in query:
    sc = {}
    try:
        sc = json.loads(r.score_json)
    except Exception:
        sc = {}
    rows.append({
        "id": r.id,
        "filename": r.filename,
        "date": r.created_at,
        "score": sc.get("final_score")
    })

df = pd.DataFrame(rows)
st.dataframe(df)
