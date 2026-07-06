import os
from dotenv import load_dotenv  # pip install python-dotenv

# Load variables from .env file into environment
load_dotenv()

# ---------- Chunking Settings ----------

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50