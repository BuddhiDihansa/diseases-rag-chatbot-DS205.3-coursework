"""
reranker.py
Member 2 - Retrieval & Vector Database

Purpose: Second-pass re-ranking of the hybrid search shortlist.
"""

from typing import List, Dict, Any
from sentence_transformers import CrossEncoder


class CrossEncoderReranker:
    """
    Wraps a cross-encoder model to re-rank a shortlist of retrieved
    chunks against the original query.
    """

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):
        self.model_name = model_name
        print(
            f"[CrossEncoderReranker] Loading cross-encoder model: "
            f"{model_name} ..."
        )
        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Re-score candidate chunks using a cross encoder and
        return the best results.
        """

        if not candidates:
            return []

        # Create query-passage pairs
        pairs = [
            (query, candidate["text"])
            for candidate in candidates
        ]

        # Predict relevance scores
        rerank_scores = self.model.predict(pairs)

        reranked = []

        for candidate, score in zip(candidates, rerank_scores):
            enriched = dict(candidate)

            enriched["hybrid_score"] = candidate.get("score")
            enriched["rerank_score"] = float(score)

            reranked.append(enriched)

        # Sort by reranker score
        reranked.sort(
            key=lambda x: x["rerank_score"],
            reverse=True
        )

        # Filter low-quality chunks
        MIN_RERANK_SCORE = 0.55

        filtered = [
            r
            for r in reranked
            if r["rerank_score"] >= MIN_RERANK_SCORE
        ]

        # Fallback if everything is filtered out
        if not filtered:
            filtered = reranked[:3]

        return filtered[:top_k]


# ------------------------------------------------------
# Standalone Test
# ------------------------------------------------------

if __name__ == "__main__":

    reranker = CrossEncoderReranker()

    fake_query = "high fever and joint pain"

    fake_candidates = [
        {
            "id": "c1",
            "text": (
                "Dengue fever causes high fever, "
                "joint pain, and rash."
            ),
            "score": 0.71
        },
        {
            "id": "c2",
            "text": (
                "Common cold symptoms include "
                "runny nose and mild cough."
            ),
            "score": 0.65
        },
        {
            "id": "c3",
            "text": (
                "Malaria presents with fever, "
                "chills, and headache."
            ),
            "score": 0.68
        }
    ]

    results = reranker.rerank(
        fake_query,
        fake_candidates,
        top_k=2
    )

    print("\nTop Results:\n")

    for result in results:
        print(
            result["id"],
            result["rerank_score"],
            "|",
            result["text"][:50]
        )