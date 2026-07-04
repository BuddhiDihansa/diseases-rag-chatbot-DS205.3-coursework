"""
Medical Disease RAG System — Streamlit Frontend
Entry point: streamlit run main.py
"""
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from app.ingestion.pdf_loader import PDFIngester
from app.vectorstore.chroma_store import ChromaVectorStore
from app.retrieval.retriever import MedicalRetriever
from app.generation.llm_generator import GroqGenerator

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Medical RAG Assistant",
    page_icon="🏥",
    layout="wide",
)

st.title("🏥 Medical Disease RAG System")
st.caption("Medical knowledge base loaded automatically → Ask symptom-based questions → Get grounded answers")
# ── Initialise components (cached so they persist across reruns) ──────────────
@st.cache_resource
def get_components():
    persist_dir = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    collection  = os.getenv("COLLECTION_NAME", "medical_docs")
    embed_model = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")

    store     = ChromaVectorStore(persist_dir, collection, embed_model)
    ingester  = PDFIngester(chunk_size=500, chunk_overlap=100)
    retriever = MedicalRetriever(store)
    generator = GroqGenerator()
    return store, ingester, retriever, generator

store, ingester, retriever, generator = get_components()

# ── Auto-ingest PDFs from /pdfs folder ───────────────────────────────────────
PDF_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pdfs")

def auto_ingest(store, ingester):
    """Automatically ingest all PDFs from the pdfs/ folder on startup."""
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
        return 0
    
    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]
    if not pdf_files:
        return 0
    
    total_chunks = 0
    for pdf_file in pdf_files:
        pdf_path = os.path.join(PDF_FOLDER, pdf_file)
        chunks = ingester.load(pdf_path)
        store.add_documents(chunks)
        total_chunks += len(chunks)
    return total_chunks

# Run auto-ingestion only if DB is empty
if store.count() == 0:
    with st.spinner("📚 Loading medical knowledge base from pdfs/ folder..."):
        total = auto_ingest(store, ingester)
        if total > 0:
            st.success(f"✅ Auto-ingested {total} chunks from pdfs/ folder!")
        else:
            st.warning("⚠️ No PDFs found in pdfs/ folder. Please add PDFs and restart.")

# ── Sidebar: just show status ─────────────────────────────────────────────────
with st.sidebar:
    st.header("📊 Knowledge Base Status")
    st.metric("Chunks in DB", store.count())
    st.info(f"PDFs loaded from: pdfs/ folder")
    
    if st.button("🗑️ Clear & Re-ingest"):
        store.clear()
        st.warning("Cleared. Restart the app to re-ingest.")
        st.rerun()

# ── Main Chat Area ────────────────────────────────────────────────────────────
st.header("💬 Ask About Symptoms or Diseases")

# Maintain chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("retrieved_chunks"):
            with st.expander("🔍 Retrieved Chunks (Traceability)", expanded=False):
                for i, chunk in enumerate(msg["retrieved_chunks"], 1):
                    st.markdown(f"**Chunk {i}** | Source: `{chunk['metadata'].get('source')}` | Page: `{chunk['metadata'].get('page')}` | Distance: `{chunk['distance']:.4f}`")
                    st.text(chunk["text"][:300] + "...")
                    st.divider()

# Chat input
if query := st.chat_input("Describe symptoms or ask a medical question..."):
    if store.count() == 0:
        st.error("⚠️ No documents in the knowledge base. Please add PDFs to the pdfs/ folder and restart.")        st.stop()

    # Show user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # RAG pipeline: Retrieve → Format → Generate
    with st.chat_message("assistant"):
        with st.spinner("Searching medical knowledge base..."):
            # STEP 1: RETRIEVAL (traceable)
            chunks = retriever.retrieve(query, n_results=5)
            context = retriever.format_context(chunks)

            # STEP 2: GENERATION (grounded)
            answer = generator.generate(query, context)

        st.markdown(answer)

        # Show retrieved chunks for full traceability (required for Viva)
        with st.expander("🔍 Retrieved Chunks (Traceability)", expanded=False):
            for i, chunk in enumerate(chunks, 1):
                st.markdown(f"**Chunk {i}** | Source: `{chunk['metadata'].get('source')}` | Page: `{chunk['metadata'].get('page')}` | Distance: `{chunk['distance']:.4f}`")
                st.text(chunk["text"][:300] + "...")
                st.divider()

    # Save to session history
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "retrieved_chunks": chunks,
    })
