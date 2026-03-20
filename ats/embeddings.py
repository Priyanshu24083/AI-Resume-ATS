# ats/embeddings.py
from sentence_transformers import SentenceTransformer
import numpy as np
from pathlib import Path
import hashlib

MODEL_NAME = "all-MiniLM-L6-v2"
CACHE_DIR = Path(".ats_cache")
CACHE_DIR.mkdir(exist_ok=True)

_model = None

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def _hash_text(t: str) -> str:
    h = hashlib.sha256(t.encode("utf-8")).hexdigest()
    return h

def embed_text(text: str, use_cache=True) -> np.ndarray:
    key = _hash_text(text)
    path = CACHE_DIR / f"{key}.npy"
    if use_cache and path.exists():
        return np.load(path)
    model = _get_model()
    vec = model.encode(text, convert_to_numpy=True, show_progress_bar=False)
    if use_cache:
        np.save(path, vec)
    return vec
