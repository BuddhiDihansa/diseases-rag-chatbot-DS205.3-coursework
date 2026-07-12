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

    # Contextual retrieval fix: many chunks (e.g. a bullet list under a
    # generic section heading like "3.3 Management of children who do
    # not need admission") never mention the disease name at all - it's
    # only implied by the source PDF's title. A query like "What should
    # someone with dengue avoid?" then fails to match that chunk on
    # BM25 or embedding similarity, even though the chunk is exactly
    # the right answer. Prepending a short document-derived context
    # string to the text BEFORE embedding fixes this without changing
    # what's shown to the user (the original c.text is still stored/
    # displayed; only the embedding input changes).
    def _document_title(filename: str) -> str:
        return filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ")

    embedding_inputs = [
        f"Source document: {_document_title(c.source_document)}\n\n{c.text}"
        for c in all_chunks
    ]
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