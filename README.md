# MediGuide LK — Medical Multi-Agent RAG System

A Retrieval-Augmented Generation (RAG) system, built as a **multi-agent
pipeline**, that answers symptom-based medical questions by retrieving and
reasoning over a private corpus of disease guideline PDFs (Dengue, Diabetes,
Asthma, Heart Disease, Kidney Disease, Migraine, Influenza, Anaemia,
COVID-19, Food Allergy).

Built for **DS205.3 — Data Science with Python** coursework.

---

## Why this system exists

General-purpose LLMs cannot reliably answer domain-specific medical
questions: their training data has a cutoff date and they have no access to
authoritative, private clinical guideline documents. This system solves
that by retrieving grounded passages from a curated set of medical PDFs
before generating any answer, and by verifying every generated answer
against that retrieved context before showing it to the user.

## Architecture

```
User symptom description
        │
        ▼
 ┌───────────────┐
 │ SymptomAgent  │  structures free-text input into a clean symptom query
 └───────┬───────┘
         ▼
 ┌────────────────┐
 │ RetrieverAgent │  hybrid search (BM25 + FAISS vector) + cross-encoder rerank
 └───────┬────────┘
         ▼
 ┌────────────────┐
 │ ReasoningAgent │  generates an answer using ONLY the retrieved context
 └───────┬────────┘
         ▼
 ┌─────────────────┐        not faithful ──► retry ReasoningAgent
 │VerificationAgent│                          with feedback (reflection loop,
 └───────┬─────────┘                          up to N attempts)
         ▼
   Final answer (+ faithfulness verdict, shown to user)
```

**Data pipeline** (run once via `build_database.py`):

```
PDF (data/raw_pdf/) → PDFLoader (PyMuPDF, text + tables)
                    → TextCleaner
                    → TextChunker (500 chars, 50 overlap, word-boundary snapped)
                    → EmbeddingService (all-MiniLM-L6-v2)
                    → VectorStore (FAISS, persisted to data/faiss_db/)
                    → BM25 index (persisted to data/bm25_data.pkl)
```

## Project structure

```
agents/         SymptomAgent, ReasoningAgent, VerificationAgent (+ BaseAgent ABC)
ingestion/      PDFLoader, TextCleaner, TextChunker
retrieval/      EmbeddingService, VectorStore (FAISS), HybridSearch, CrossEncoderReranker, RetrieverAgent
services/       LLMClient (Groq API wrapper), MedicalAIPipeline (orchestrator)
evaluation/     ground_truth.json, Evaluator, run_evaluation.py
utils/          custom exceptions, logger
config/         setting.py — all tunable values in one place
tests/          pytest unit tests per module
data/raw_pdf/   source medical guideline PDFs (private corpus)
```

## Setup

1. **Clone and create a virtual environment**
   ```bash
   git clone <your-repo-url>
   cd diseases-rag-chatbot-DS205.3-coursework
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your API key**
   ```bash
   cp .env.example .env
   # then edit .env and paste your Groq API key
   ```
   Get a free key at https://console.groq.com/keys

4. **Build the vector database** (run once, or whenever PDFs change)
   ```bash
   python build_database.py
   ```

5. **Run the chatbot**
   ```bash
   python main.py
   ```

6. **Run the evaluation suite**
   ```bash
   python -m evaluation.run_evaluation
   ```
   This runs all ground-truth questions through the full pipeline, scores
   each answer (semantic similarity + keyword overlap), and writes
   `evaluation/results.csv`.

7. **Run the tests**
   ```bash
   pytest tests/ -v
   ```

## Key design decisions

- **Hybrid search (BM25 + vector) with cross-encoder reranking** — vector
  search alone can miss exact keyword matches (drug names, disease names);
  BM25 catches those. A cross-encoder then re-scores the combined shortlist
  for a final precision boost.
- **FAISS instead of ChromaDB** — avoids a C++ build toolchain requirement
  on Windows, while still meeting the persistent vector storage requirement.
- **Reflection loop** — if `VerificationAgent` finds the generated answer
  isn't fully supported by the retrieved context, the pipeline retries
  `ReasoningAgent` with explicit feedback about what was wrong (up to
  `max_reflection_attempts`) instead of returning a possibly-hallucinated
  answer immediately.
- **Dependency Injection throughout** — every agent and service accepts its
  dependencies via the constructor, so components can be tested and swapped
  independently.

## Known limitations / future work

- Source citations currently identify the source **document**, not the
  specific page number (page-level tracking would require the PDF loader to
  keep per-page boundaries rather than merging a document's pages into one
  text block).
- Faithfulness verification uses the same LLM that generates the answer;
  a separate/stronger judge model would reduce shared-bias risk.
- See the Technical Design & Evaluation Report, Section VI, for further
  planned improvements (multimodal support, additional agentic steps).
