# MediGuide LK — Medical AI Multi-Agent RAG System

A Retrieval-Augmented Generation (RAG) system that answers medical questions by retrieving grounded context from a private corpus of medical guideline documents, then reasoning over that context using a multi-agent pipeline — rather than relying on an LLM's raw (and potentially outdated or hallucinated) knowledge.

Built for **DS205.3 — Data Science with Python** (Coursework Assessment 1).

## Problem statement

Standard LLMs cannot be trusted for domain-specific medical guidance because they:
- Have a training data cutoff and cannot access newly published or region-specific guidelines
- Have no access to private/specialized documents (e.g. national treatment guidelines)
- Can hallucinate confident-sounding but incorrect medical claims

This system addresses that gap by grounding every answer in retrieved excerpts from real medical documents, and by verifying that the generated answer is actually supported by that retrieved context.

## Architecture

```
User Query
   │
   ▼
SymptomAgent          — extracts structured symptoms from free text
   │
   ▼
RetrieverAgent         — hybrid search (BM25 + FAISS vector search)
   │                       over the persisted vector store
   ▼
ReasoningAgent         — generates a grounded answer using ONLY
   │                       the retrieved context
   ▼
VerificationAgent      — checks the answer against the retrieved
   │                       context for unsupported claims
   ▼
Final Answer + Verification Verdict
```

See `reports/architecture_diagram.png` for the full data flow diagram (PDF → chunks → embeddings → vector store → LLM).

### Why these design choices

| Decision | Reasoning |
|---|---|
| FAISS instead of ChromaDB | ChromaDB's `chroma-hnswlib` dependency requires a C++ compiler to build on Windows. FAISS ships prebuilt wheels, avoiding install friction across the team. |
| Hybrid search (BM25 + vector) | Vector search captures semantic meaning but can miss exact keyword matches (disease/drug names). BM25 catches those. Combining both improves retrieval quality. |
| Chunk size 500 / overlap 50 | Balances keeping enough context per chunk against retrieval precision. Tested against 300 and 800 as alternatives (see report). |
| Groq API (LLaMA 3.3 70B) | OpenAI-compatible API format, generous free tier, fast inference — suitable for a student project budget. |
| Abstract `BaseAgent` class | Enforces a consistent `.run()` interface across all agents so the pipeline can call any agent polymorphically without knowing its internals. |

## Project structure

```
medical_ai/
├── agents/              # SymptomAgent, ReasoningAgent, VerificationAgent (+ BaseAgent ABC)
├── ingestion/           # PDF loading, text cleaning, chunking
├── retrieval/           # Embeddings, FAISS vector store, BM25 hybrid search, RetrieverAgent
├── services/            # LLM API client, pipeline orchestrator
├── evaluation/          # Ground-truth Q&A dataset, evaluator, evaluation runner
├── config/              # Centralized settings
├── utils/               # Shared logging utility
├── tests/               # pytest test suite for agents, retrieval, ingestion, evaluation
├── data/                # Raw PDFs, processed chunks, persisted FAISS index (gitignored)
├── reports/             # Architecture diagram and supporting report assets
├── build_database.py    # One-time / on-demand script: PDF → chunks → embeddings → FAISS + BM25
├── main.py               # Entry point — interactive CLI
└── requirements.txt
```

## Setup

**Requirements:** Python 3.10+

1. Clone the repository and create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the environment template and add your API key:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and set `LLM_API_KEY` to your own Groq API key (get one free at https://console.groq.com).

4. Add source PDFs to `data/raw_pdfs/` (medical guideline documents).

5. Build the vector database (run once, or whenever the PDFs change):
   ```bash
   python build_database.py
   ```

6. Run the system:
   ```bash
   python main.py
   ```

## Running the evaluation

```bash
python -m evaluation.run_evaluation
```

This runs every question in `evaluation/ground_truth.json` through the full pipeline, scores each answer against the expected answer using semantic similarity + keyword overlap, and writes a results table to `evaluation/results.csv` — used directly in the report's Empirical Evaluation section.

## Running tests

```bash
pytest tests/ -v
```

## Team contributions

| Member | Area |
|---|---|
| Member 1 | Data engineering — PDF ingestion, text cleaning, chunking |
| Member 2 | Retrieval — embeddings, FAISS vector store, hybrid (BM25 + vector) search |
| Member 3 | Agent logic — symptom extraction, grounded reasoning, hallucination verification |
| Member 4 | Evaluation — ground-truth dataset, scoring framework, report |

## Disclaimer

This system is a student coursework project for educational purposes. It is **not a substitute for professional medical advice, diagnosis, or treatment.**