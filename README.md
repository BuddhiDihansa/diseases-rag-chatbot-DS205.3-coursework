<<<<<<< HEAD
# 🏥 Medical Disease RAG System
**DS205.3 – Data Science with Python | Group Coursework**

A Retrieval-Augmented Generation (RAG) system for medical disease diagnosis assistance. Users upload medical PDFs and query the system with symptoms to receive grounded, traceable answers.

---

## 🏗️ Architecture

```
User Query (Symptoms)
        │
        ▼
┌──────────────────┐
│  Streamlit UI    │  ← main.py
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  MedicalRetriever│  ← app/retrieval/retriever.py
│  (Query Embed)   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  ChromaVectorStore│ ← app/vectorstore/chroma_store.py
│  (Persistent DB) │   ChromaDB on disk
└────────┬─────────┘
         │ Top-5 chunks
         ▼
┌──────────────────┐
│  GroqGenerator   │  ← app/generation/llm_generator.py
│  llama3-8b       │
└────────┬─────────┘
         │
         ▼
   Grounded Answer (with source citations)
```

## 📁 Project Structure

```
medical_rag/
├── main.py                          ← Streamlit entry point
├── requirements.txt
├── .env.example
├── app/
│   ├── ingestion/
│   │   ├── base.py                  ← Abstract Base Class
│   │   └── pdf_loader.py            ← PyMuPDF PDF loader
│   ├── vectorstore/
│   │   ├── base.py                  ← Abstract Base Class
│   │   └── chroma_store.py          ← ChromaDB persistent store
│   ├── retrieval/
│   │   ├── base.py                  ← Abstract Base Class
│   │   └── retriever.py             ← Medical retriever with traceability
│   ├── generation/
│   │   ├── base.py                  ← Abstract Base Class
│   │   └── llm_generator.py         ← Groq LLM generator
│   └── evaluation/
│       └── evaluator.py             ← Ground-truth evaluation script
└── data/
    ├── ground_truth.json            ← 10 Q&A pairs for evaluation
    └── eval_results.json            ← Generated after running evaluator
```

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone <your-github-repo-url>
cd medical_rag
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```
Get a free Groq API key at: https://console.groq.com

### 5. Run the application
```bash
streamlit run main.py
```

### 6. Run evaluation
```bash
python -m app.evaluation.evaluator
```

---

## 🔑 Key Design Decisions

| Decision | Choice | Justification |
|---|---|---|
| PDF Parser | PyMuPDF | Best text extraction fidelity for medical PDFs |
| Embeddings | all-MiniLM-L6-v2 | Free, runs locally, strong semantic similarity |
| Vector Store | ChromaDB (persistent) | Survives between sessions; cosine similarity |
| LLM | Groq llama3-8b | Free tier, low latency, grounded by strict prompt |
| Chunking | 500 chars / 100 overlap | Balances context richness and retrieval precision |

## 🧪 Evaluation

The system is evaluated using 10 ground-truth Q&A pairs scored by an LLM judge (0-10 faithfulness scale). Results are saved to `data/eval_results.json`.

---

## ⚠️ Disclaimer
This system is for educational purposes only. It is not a substitute for professional medical advice.
=======
# diseases-rag-chatbot-DS205.3-coursework
A Hybrid RAG Chatbot for Diseases and Symptoms 
>>>>>>> 28ec13da28a7e3a6dd858bbef1a3eab0a5196848
