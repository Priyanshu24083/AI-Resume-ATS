# ats/gemini_client.py
import os

try:
    from google import genai
except Exception:
    genai = None

# Model fallback: use gemini-1.5-flash if available; default to gemini-1.0-pro if not.
MODEL_NAME = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")


def explain_with_gemini(resume_text: str, jd_text: str, score_breakdown: dict) -> str:
    """
    Uses Google GenAI SDK. Priority:
      1. Streamlit sets GEMINI_API_KEY in env (session override)
      2. OS environment variable GEMINI_API_KEY
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not genai:
        return "Gemini not configured."

    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""
You are an assistant that inspects a resume and a job description.
Produce 4-6 short bullet points:
- Top matched skills
- Missing important skills
- Why the resume received its score
- One actionable improvement

Job Description:
{jd_text}

Resume:
{resume_text}

Score Breakdown:
{score_breakdown}

Respond only as short bullets.
"""
        # Use the generation API
        resp = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        # The response object structure may vary by genai version; this accesses text safely:
        text = ""
        if hasattr(resp, "text"):
            text = resp.text
        else:
            # fallback reading choices
            try:
                text = resp.generations[0].text
            except Exception:
                text = str(resp)
        return text.strip()
    except Exception as e:
        return f"Gemini API error: {e}"
