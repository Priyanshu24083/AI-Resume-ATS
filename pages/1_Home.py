import streamlit as st

# Page config (only once per page)
st.set_page_config(
    page_title="AI Resume ATS",
    layout="wide"
)

# -------------------------
# HERO SECTION
# -------------------------
st.markdown(
    """
    <h1 style='text-align: center;'>AI-Based Resume Analysis & Feedback System</h1>
    <p style='text-align: center; font-size:18px;'>
    A hybrid ATS using semantic scoring, ranking, and Gemini-powered feedback
    </p>
    """,
    unsafe_allow_html=True
)

st.image(
    "assets/hero.jpg",
    use_container_width=True
)

st.markdown("---")

# -------------------------
# CALL TO ACTION
# -------------------------
st.success(
    "👉 Use the sidebar to upload resumes and job descriptions to get started."
)
