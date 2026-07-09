"""
reranker.py
Member 2 - Retrieval & Vector Database

Purpose: Second-pass re-ranking of the hybrid search shortlist.

Why this exists: BM25 and vector search both score a query against a
chunk WITHOUT ever looking at the two together - BM25 counts keyword
overlap, and vector search compares two separate embeddings computed
in isolation. A cross-encoder instead reads the (query, chunk) PAIR
together in a single forward pass, so it can pick up on relationships
neither method alone can see (e.g. "does this chunk actually answer
THIS specific question", not just "does it share words/topic"). This
makes it meaningfully more accurate - the trade-off is that it's too
slow to run over an entire corpus, so it's only used to re-score a
small shortlist (typically 10-20 candidates) that hybrid search has
already narrowed things down to.

Flow: HybridSearch.search() casts a wide net (top_k * 2) -> this
reranker re-scores just that shortlist -> only the best few chunks
(after re-ranking) are passed to the ReasoningAgent.
"""

from typing import List, Dict, Any
from sentence_transformers import CrossEncoder  # pip install sentence-transformers


class CrossEncoderReranker:
    """
    Wraps a cross-encoder model to re-rank a shortlist of retrieved
    chunks against the original query.

    Dependency Injection: model_name passed in via constructor, so
    tests can swap in a lighter/mock model without touching the
    RetrieverAgent or HybridSearch code that uses this class.
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        print(f"[CrossEncoderReranker] Loading cross-encoder model: {model_name} ...")
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, candidates: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Re-scores a shortlist of candidate chunks against the query and
        returns only the best top_k, re-sorted by the cross-encoder's score.

        candidates: list of {"id":..., "text":..., "metadata":..., "score":...}
        as produced by HybridSearch.search() - the "score" field here is the
        hybrid BM25+vector score, kept as "hybrid_score" for comparison/report
        purposes, but ranking is now driven entirely by the cross-encoder.

        Returns the same dict shape, with an added "rerank_score" field, so
        RetrieverAgent/ReasoningAgent don't need to change how they read
        chunk "text" or "metadata".
        """
        if not candidates:
            return []

        # CrossEncoder.predict() expects a list of (query, passage) pairs
        pairs = [(query, c["text"]) for c in candidates]
        rerank_scores = self.model.predict(pairs)

        reranked = []
        for candidate, score in zip(candidates, rerank_scores):
            enriched = dict(candidate)
            enriched["hybrid_score"] = candidate.get("score")
            enriched["rerank_score"] = float(score)
            reranked.append(enriched)

        reranked.sort(key=lambda x: x["rerank_score"], reverse=True)
        return reranked[:top_k]


# Example usage (for testing this file individually)
if __name__ == "__main__":
    reranker = CrossEncoderReranker()

    fake_query = "high fever and joint pain"
    fake_candidates = [
        {"id": "c1", "text": "Dengue fever causes high fever, joint pain, and rash.", "score": 0.71},
        {"id": "c2", "text": "Common cold symptoms include runny nose and mild cough.", "score": 0.65},
        {"id": "c3", "text": "Malaria presents with fever, chills, and headache.", "score": 0.68},
    ]

    results = reranker.rerank(fake_query, fake_candidates, top_k=2)
    for r in results:
        print(r["id"], r["rerank_score"], "|", r["text"][:50])