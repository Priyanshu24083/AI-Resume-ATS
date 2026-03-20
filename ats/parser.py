# ats/parser.py
from pathlib import Path
from pdfminer.high_level import extract_text as extract_text_pdf
import docx
import chardet

def read_pdf(path: str) -> str:
    try:
        return extract_text_pdf(path) or ""
    except Exception as e:
        raise RuntimeError(f"PDF read error: {e}")

def read_docx(path: str) -> str:
    try:
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs if p.text)
    except Exception as e:
        raise RuntimeError(f"DOCX read error: {e}")

def read_txt(path: str) -> str:
    raw = Path(path).read_bytes()
    enc = chardet.detect(raw)["encoding"] or "utf-8"
    return raw.decode(enc, errors="ignore")

def extract_text(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    ext = p.suffix.lower()
    if ext == ".pdf":
        return read_pdf(str(p))
    if ext in {".docx", ".doc"}:
        return read_docx(str(p))
    return read_txt(str(p))
