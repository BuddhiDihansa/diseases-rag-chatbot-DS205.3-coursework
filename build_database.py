"""
build_database.py
Run this ONCE (or whenever PDFs change) to process real PDFs and
build the vector database. This connects Member 1's ingestion work
with Member 2's retrieval work.

Flow: PDF -> extract text -> clean -> chunk -> embed -> store in FAISS + BM25

Run with: python build_database.py
(run from the project root, medical_ai/ folder)
"""

from ingestion.pdf_loader import PDFLoader
from ingestion.text_cleaner import TextCleaner
from ingestion.chunker import TextChunker, is_boilerplate_chunk
from retrieval.embedding_service import EmbeddingService
from retrieval.vector_store import VectorStore
from retrieval.hybrid_search import HybridSearch
import pickle
import re


def build_database():
    print("=" * 60)
    print("STEP 1: Loading PDFs")
    print("=" * 60)

    loader = PDFLoader(pdf_folder="data/raw_pdf")
    raw_documents = loader.load_all_pdfs()

    if not raw_documents:
        print("No PDFs found in data/raw_pdfs/. Add at least one PDF and try again.")
        return

    print("\n" + "=" * 60)
    print("STEP 2: Cleaning text")
    print("=" * 60)

    cleaner = TextCleaner()
    cleaned_documents = {
        filename: cleaner.clean(text)
        for filename, text in raw_documents.items()
    }

    print("\n" + "=" * 60)
    print("STEP 3: Chunking text")
    print("=" * 60)

    chunker = TextChunker(chunk_size=500, chunk_overlap=50)
    all_chunks = chunker.chunk_multiple_documents(cleaned_documents)

    print(f"\nTotal chunks created: {len(all_chunks)}")

    # Drop front-matter/administrative chunks (title pages, committee/
    # acknowledgements lists, forewords, ISBN/TOC pages) before they
    # get embedded. These carry no clinical information but were
    # observed outranking genuinely relevant clinical chunks in
    # retrieval (e.g. a Director's foreword mentioning "dengue" several
    # times outscored the actual DF/DHF symptom list for "What are the
    # symptoms of Dengue fever?"). See chunker.py's is_boilerplate_chunk
    # docstring for the detection heuristic.
    before_count = len(all_chunks)
    all_chunks = [c for c in all_chunks if not is_boilerplate_chunk(c.text)]
    dropped = before_count - len(all_chunks)
    print(f"Filtered out {dropped} boilerplate/front-matter chunks "
          f"({before_count} -> {len(all_chunks)} chunks)")

    print("\n" + "=" * 60)
    print("STEP 4: Embedding chunks")
    print("=" * 60)

    embedding_service = EmbeddingService()

    chunk_ids = [c.chunk_id for c in all_chunks]

    # Contextual retrieval fix (v3 - EXPLICIT MAPPING):
    # v1 prepended "Source document: <title>" to EVERY chunk - didn't
    # change relative ranking WITHIN a document (every chunk in it got
    # the same boost) and perturbed embeddings of chunks that already
    # retrieved fine, causing regressions elsewhere (mild-asthma-
    # treatment and diabetic-diet answers got worse in the 2nd eval run).
    #
    # v2 tried to auto-extract a "disease keyword" from each filename
    # and only prefix chunks missing it. This broke in two ways:
    #  - "fever" is too generic: it appears in an unrelated paracetamol-
    #    dosing chunk, so that chunk was wrongly judged as "already
    #    mentioning the disease" and skipped - the exact bug we're
    #    trying to fix.
    #  - GINA-2026-Strategy-Report-WMS.pdf never contains the word
    #    "asthma" in its filename at all (GINA = Global INitiative for
    #    Asthma, an acronym) - filename parsing can't recover a
    #    keyword that isn't there.
    #
    # v3 uses an explicit, human-curated mapping instead of guessing.
    # There are only ~14 source PDFs, so hand-mapping each to its real
    # topic is trivial and far more reliable than filename heuristics.
    # Update this dict if new PDFs are added to data/raw_pdf/.
    _DOCUMENT_TOPIC = {
        "3426_dmkg-treatment-of-migraine-attacks-and-prevention-of-migraine.pdf": "migraine",
        "COVID 19.pdf": "COVID-19",
        "GINA-2026-Strategy-Report-WMS.pdf": "asthma",
        "Guidelines-on-Management-of-Dengue-Fever.pdf": "dengue fever",
        "Heart Disease.pdf": "heart disease",
        "Influenza-Diagnosis-and-Treatment.pdf": "influenza",
        "Influenza-guidelines_-25April-2023-final.pdf": "influenza",
        "Migraine.pdf": "migraine",
        "NSD610-014-CYANS-Management-of-food-allerg.pdf": "food allergy",
        "anaemia-symptoms-causes-prevention-diagnosis-and-treatment.pdf": "anaemia",
        "diabetescare-guideline-may-2026.pdf": "diabetes",
        "heart disease cad-guide.pdf": "heart disease",
        "kidney disease.pdf": "kidney disease",
        "kidney disease_full_guideline.pdf": "kidney disease",
        "nhlbi-ospeec-your-guide-to-anemia-booklet-release-508.pdf": "anaemia",
    }

    def _topic_for(filename: str) -> str:
        return _DOCUMENT_TOPIC.get(filename, filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " "))

    def _needs_context_prefix(chunk_text: str, filename: str) -> bool:
        topic = _topic_for(filename)
        return topic.lower() not in chunk_text.lower()

    embedding_inputs = []
    prefixed_count = 0
    for c in all_chunks:
        if _needs_context_prefix(c.text, c.source_document):
            embedding_inputs.append(f"Topic: {_topic_for(c.source_document)}\n\n{c.text}")
            prefixed_count += 1
        else:
            embedding_inputs.append(c.text)
    print(f"Added contextual prefix to {prefixed_count}/{len(all_chunks)} chunks "
          f"(only those missing their document's topic name).")

    texts = [c.text for c in all_chunks]  # original text: stored & shown to user, unchanged
    metadatas = [{"source_document": c.source_document} for c in all_chunks]

    embeddings = embedding_service.embed_batch(embedding_inputs)

    print("\n" + "=" * 60)
    print("STEP 5: Storing in vector database")
    print("=" * 60)

    vector_store = VectorStore(persist_directory="data/faiss_db")
    vector_store.reset()  # clean rebuild each time this script runs
    vector_store.add_chunks(chunk_ids, texts, embeddings, metadatas)

    print("\n" + "=" * 60)
    print("STEP 6: Building BM25 index")
    print("=" * 60)

    hybrid_search = HybridSearch(vector_store=vector_store, embedding_service=embedding_service)
    hybrid_search.build_bm25_index(chunk_ids, texts, metadatas, index_texts=embedding_inputs)

    # Save the BM25 index data so main.py can load it without rebuilding.
    # FIXED: "metadatas" is now included - without it, BM25-only matches
    # (i.e. chunks found by keyword search but not by vector search) lost
    # their source_document citation and showed up as "unknown source" in
    # the retrieved context trace, weakening the Traceability requirement.
    with open("data/bm25_data.pkl", "wb") as f:
        pickle.dump(
            {
                "chunk_ids": chunk_ids,
                "texts": texts,
                "metadatas": metadatas,
                # context-prefixed versions of `texts`, used to rebuild the
                # BM25 index identically when RetrieverAgent loads this file
                # at runtime (see retriever_agent.py) - without this, the
                # contextual-retrieval fix above would only apply the one
                # time build_database.py itself runs, not on every app start.
                "index_texts": embedding_inputs,
            },
            f,
        )

    print("\n" + "=" * 60)
    print(f"DATABASE BUILD COMPLETE - {len(all_chunks)} chunks stored and indexed")
    print("=" * 60)


if __name__ == "__main__":
    build_database()