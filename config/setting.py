
"""
settings.py
Shared configuration for the entire project.

Purpose: Centralize all configurable values (API keys, model names,
chunk sizes, paths) in ONE place. Instead of hardcoding these values
in every file, other modules import from here. This makes the system
easier to configure, test, and explain in the Viva.

Values are loaded from environment variables (.env file) where sensitive,
with sensible defaults for everything else.
"""

import os
from dotenv import load_dotenv  # pip install python-dotenv

# Load variables from .env file into environment
load_dotenv()


# ---------- Chunking Settings ----------

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# ---------- LLM Settings ----------
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-6")
LLM_MAX_TOKENS = 500


# ---------- Embedding Settings ----------
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


# ---------- Vector Database Settings ----------
# Using FAISS instead of ChromaDB (avoids needing a C++ compiler on Windows)
VECTOR_DB_PERSIST_DIR = os.getenv("VECTOR_DB_PERSIST_DIR", "data/faiss_db")
VECTOR_DB_COLLECTION_NAME = "medical_documents"
EMBEDDING_DIMENSION = 384  # all-MiniLM-L6-v2 produces 384-dimension vectors


# ---------- Chunking Settings ----------
# Tested 300 / 500 / 800 during development - 500 gave the best balance
# between keeping enough context per chunk and retrieval precision.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


# ---------- Hybrid Search Settings ----------
# Weights must sum to 1.0. Vector search weighted higher since
# semantic meaning matters more than exact keyword matches for
# symptom-based queries (users describe symptoms in their own words).
BM25_WEIGHT = 0.4
VECTOR_WEIGHT = 0.6
TOP_K_RESULTS = 5


# ---------- Data Paths ----------
RAW_PDF_DIR = "data/raw_pdf"
PROCESSED_DATA_DIR = "data/processed"
GROUND_TRUTH_PATH = "evaluation/ground_truth.json"
EVALUATION_RESULTS_PATH = "evaluation/results.csv"


# ---------- Validation ----------
def validate_settings():
    """
    Call this at startup to catch missing config early,
    instead of failing later with a confusing error.
    """
    if not LLM_API_KEY:
        print("WARNING: LLM_API_KEY is not set. Check your .env file.")

    if not os.path.exists(RAW_PDF_DIR):
        print(f"WARNING: {RAW_PDF_DIR} does not exist yet. Create it and add PDFs.")


if __name__ == "__main__":
    validate_settings()
    print(f"LLM Model: {LLM_MODEL}")
    print(f"Embedding Model: {EMBEDDING_MODEL}")
    print(f"Chunk Size: {CHUNK_SIZE}, Overlap: {CHUNK_OVERLAP}")
    print(f"BM25 Weight: {BM25_WEIGHT}, Vector Weight: {VECTOR_WEIGHT}")

