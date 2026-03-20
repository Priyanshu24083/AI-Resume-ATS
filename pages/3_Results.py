# pages/3_Results.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

from ats.db import init_db
from ats.gemini_client import explain_with_gemini

st.title("Results Dashboard")

# fetch results from session_state or DB
results = st.session_state.get("results", None)

if results is None:
    # load latest from DB
    Session = init_db("sqlite:///ats_results.db")
    session = Session()
    rows = session.query().all() if False else []  # avoid heavy query; rely on session_state for simplicity
    st.info("No recent run in session. Run resumes on Upload page first.")
else:
    # convert to dataframe for ranking
    df_rows = []
    for r in results:
        parsed = r["parsed"]
        score = r["score"]
        df_rows.append({
            "filename": r["file"],
            "name": parsed.get("name",""),
            "semantic": score.get("semantic_pct",0),
            "keyword": score.get("keyword_pct",0),
            "heuristic": score.get("heuristic_pct",0),
            "institution": score.get("institution_score_pct",0),
            "final": score.get("final_score",0),
            "gemini": r.get("gemini","")
        })
    df = pd.DataFrame(df_rows).sort_values("final", ascending=False).reset_index(drop=True)
    st.markdown("### Ranking")
    df_display = df[["filename","final"]].rename(columns={"final":"Final Score"})
    st.dataframe(df_display.style.format({"Final Score":"{:.2f}"}))

    # show full details for each resume in ranked order
    for idx, row in df.iterrows():
        st.markdown("---")
        st.header(f"{idx+1}. {row['filename']} — Score: {row['final']:.2f}")
        # radar chart
        categories = ["Semantic","Keyword","Heuristic"]
        values = [row["semantic"], row["keyword"], row["heuristic"]]
        fig = go.Figure(data=[go.Scatterpolar(r=values+[values[0]], theta=categories+[categories[0]], fill='toself')])
        fig.update_layout(polar=dict(radialaxis=dict(range=[0,100])), showlegend=False, title="Score Breakdown (Radar)")
        st.plotly_chart(fig, use_container_width=True)

        # bar chart below radar
        bar_data = {
            "metric":["Semantic","Keyword","Education","Experience","Institution","Final"],
            "value":[row["semantic"], row["keyword"], row["heuristic"]/2*100 if row["heuristic"] else 0, row["heuristic"]/2*100 if row["heuristic"] else 0, row["institution"], row["final"]]
        }
        # note: heuristic is small; here we split it to Education/Experience for visualization simplicity
        bdf = px.bar(pd.DataFrame(bar_data), x="metric", y="value", title="Section-wise Marks (Bar)")
        bdf.update_yaxes(range=[0,100])
        st.plotly_chart(bdf, use_container_width=True)

        # show Gemini output
        gem = row.get("gemini","")
        st.subheader("Gemini Explanation")
        st.write(gem or "_No explanation_")

        # Tailored Resume: ask Gemini to produce heading-wise bullet suggestions
        if gem:
            st.subheader("Tailored Resume Suggestions")
            # reuse the same gemini explanation or call more targeted prompt
            tailored = explain_with_gemini("TAILORED_REQUEST:\n"+gem, "Use JD in original run (see DB)", {"final": row["final"]})
            st.write(tailored)
