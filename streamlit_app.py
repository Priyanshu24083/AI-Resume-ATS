# streamlit_app.py
import streamlit as st

st.set_page_config(page_title="HSK ATS", layout="wide")
st.title("HSK ATS — Hybrid Semantic–Keyword–Heuristic Resume Evaluator")

st.markdown(
    "Use the left sidebar to navigate the app pages. "
    "Pages: Home, Upload & Run, Results, Database Viewer."
)

st.sidebar.markdown("HSK ATS")
