"""
debug_retrieval.py
Run this from the project root: python debug_retrieval.py

Purpose: find out WHY the "Avoid all NSAIDs and steroids" chunk isn't
showing up in the top-7 results for "What should someone with dengue
avoid?" - prints its actual rank (however far down) so we know whether
this is a ranking problem (chunk exists, just ranked low) or a chunking
problem (the sentence got split/dropped and isn't a chunk at all).
"""

import pickle
from retrieval.embedding_service import EmbeddingService
from retrieval.vector_store import VectorStore
from retrieval.hybrid_search import HybridSearch

QUERY = "What should someone with dengue avoid?"
TARGET_KEYWORDS = ["nsaid", "aspirin", "steroid"]  # any chunk containing these is the one we want


def main():
    embedding_service = EmbeddingService()
    vector_store = VectorStore(persist_directory="data/faiss_db")
    hybrid_search = HybridSearch(vector_store=vector_store, embedding_service=embedding_service)

    with open("data/bm25_data.pkl", "rb") as f:
        bm25_data = pickle.load(f)

    metadatas = bm25_data.get("metadatas")
    index_texts = bm25_data.get("index_texts")
    hybrid_search.build_bm25_index(
        bm25_data["chunk_ids"], bm25_data["texts"], metadatas, index_texts=index_texts
    )

    # Step 1: does a target chunk even exist in the corpus at all?
    print("=" * 70)
    print("STEP 1: Does the NSAID/aspirin chunk exist anywhere in the corpus?")
    print("=" * 70)
    target_chunks = [
        (cid, text) for cid, text in zip(bm25_data["chunk_ids"], bm25_data["texts"])
        if any(kw in text.lower() for kw in TARGET_KEYWORDS)
    ]
    if not target_chunks:
        print("NOT FOUND ANYWHERE. The chunking step is dropping this sentence.")
        return
    for cid, text in target_chunks:
        print(f"\nFOUND chunk_id={cid}")
        print(f"  text: {text[:300]}")

    target_ids = {cid for cid, _ in target_chunks}

    # Step 2: what rank does it get in a large-k search (bypass top_k=5 cutoff)?
    print("\n" + "=" * 70)
    print(f"STEP 2: Rank of that chunk for query: '{QUERY}' (checking top 50)")
    print("=" * 70)

    vector_results = hybrid_search.vector_search(QUERY, top_k=50)
    bm25_results = hybrid_search.bm25_search(QUERY, top_k=50)

    def find_rank(results, label):
        for rank, r in enumerate(results, start=1):
            if r["id"] in target_ids:
                print(f"  [{label}] rank {rank} of 50, score={r['score']:.3f}, id={r['id']}")
                return rank
        print(f"  [{label}] NOT in top 50 at all")
        return None

    find_rank(vector_results, "VECTOR/FAISS")
    find_rank(bm25_results, "BM25")

    print("\nIf rank is > 7 on both, top_k needs increasing or the chunk's")
    print("embedding needs stronger contextual signal. If rank is missing")
    print("from top 50 entirely, something is wrong with how it was indexed.")


if __name__ == "__main__":
    main()