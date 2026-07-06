"""
hybrid_search.py
Member 2 - Retrieval & Vector Database

Purpose: Combine BM25 (keyword-based) search with vector (semantic) search.
Why hybrid? Vector search is great for meaning/context, but can miss
exact keyword matches (e.g. specific disease names, drug names).
BM25 catches those exact matches. Combining both gives better retrieval.
"""

from typing import List, Dict, Any
from rank_bm25 import BM25Okapi  # pip install rank-bm25


class HybridSearch:
    """
    Combines BM25 keyword search results with vector search results,
    using a weighted score to rank the final results.
    """

    def __init__(self, vector_store, embedding_service, bm25_weight: float = 0.4,
                 vector_weight: float = 0.6):
        """
        vector_store: instance of VectorStore
        embedding_service: instance of EmbeddingService
        bm25_weight / vector_weight: how much each method contributes to final score
        (must sum to 1.0 - these values are worth tuning and justifying in your report)
        """
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.bm25_weight = bm25_weight
        self.vector_weight = vector_weight
        self.bm25_index = None
        self.corpus_chunks = []  # list of {"id":..., "text":...}

    def build_bm25_index(self, chunk_ids: List[str], texts: List[str]):
        """
        Build the BM25 index from all chunks.
        Must be called once after all chunks are added to the vector store.
        """
        self.corpus_chunks = [{"id": cid, "text": text} for cid, text in zip(chunk_ids, texts)]
        tokenized_corpus = [text.lower().split() for text in texts]
        self.bm25_index = BM25Okapi(tokenized_corpus)
        print(f"BM25 index built with {len(texts)} chunks.")

    def bm25_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search using BM25 keyword matching."""
        if self.bm25_index is None:
            raise ValueError("BM25 index not built yet. Call build_bm25_index() first.")

        tokenized_query = query.lower().split()
        scores = self.bm25_index.get_scores(tokenized_query)

        scored_chunks = [
            {"id": self.corpus_chunks[i]["id"], "text": self.corpus_chunks[i]["text"], "score": scores[i]}
            for i in range(len(scores))
        ]
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]

    def vector_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search using semantic vector similarity."""
        query_embedding = self.embedding_service.embed_text(query)
        results = self.vector_store.query(query_embedding, top_k=top_k)

        scored_chunks = []
        for i, chunk_id in enumerate(results["ids"][0]):
            scored_chunks.append({
                "id": chunk_id,
                "text": results["documents"][0][i],
                "score": 1 - results["distances"][0][i]  # convert distance to similarity
            })
        return scored_chunks

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Combine BM25 + vector search results using weighted scores.
        This is the main method other agents should call.
        """
        bm25_results = self.bm25_search(query, top_k=top_k * 2)
        vector_results = self.vector_search(query, top_k=top_k * 2)

        # normalize scores to 0-1 range within each method, then combine
        combined_scores = {}

        max_bm25 = max([r["score"] for r in bm25_results], default=1) or 1
        for r in bm25_results:
            normalized = r["score"] / max_bm25
            combined_scores[r["id"]] = {
                "text": r["text"],
                "score": normalized * self.bm25_weight
            }

        for r in vector_results:
            if r["id"] in combined_scores:
                combined_scores[r["id"]]["score"] += r["score"] * self.vector_weight
            else:
                combined_scores[r["id"]] = {
                    "text": r["text"],
                    "score": r["score"] * self.vector_weight
                }

        final_results = [
            {"id": cid, "text": data["text"], "score": data["score"]}
            for cid, data in combined_scores.items()
        ]
        final_results.sort(key=lambda x: x["score"], reverse=True)

        return final_results[:top_k]


# Example usage (for testing this file individually)
if __name__ == "__main__":
    print("This module needs VectorStore and EmbeddingService instances to run.")
    print("Test it together with retriever_agent.py once other modules are ready.")