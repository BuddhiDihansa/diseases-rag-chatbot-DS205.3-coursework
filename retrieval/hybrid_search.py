"""
hybrid_search.py
Member 2 - Retrieval & Vector Database

Purpose: Combine BM25 (keyword-based) search with vector (semantic) search.
Why hybrid? Vector search is great for meaning/context, but can miss
exact keyword matches (e.g. specific disease names, drug names).
BM25 catches those exact matches. Combining both gives better retrieval.

Optionally applies a third stage - cross-encoder re-ranking (see
reranker.py) - on the combined shortlist for higher precision before
the final top_k is returned.
"""

from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi  # pip install rank-bm25
import numpy as np


class HybridSearch:
    """
    Combines BM25 keyword search results with vector search results,
    using a weighted score to rank the final results. Optionally
    re-ranks the combined shortlist with a cross-encoder for higher
    precision (see search() and the reranker param), and optionally
    applies MMR diversification as a final selection step (see
    use_mmr param and _mmr_select() below).
    """

    def __init__(self, vector_store, embedding_service, bm25_weight: float = 0.4,
                 vector_weight: float = 0.6, reranker: Optional[Any] = None,
                 use_mmr: bool = False, mmr_lambda: float = 0.7):
        """
        vector_store: instance of VectorStore
        embedding_service: instance of EmbeddingService
        bm25_weight / vector_weight: how much each method contributes to final score
        (must sum to 1.0 - these values are worth tuning and justifying in your report)

        Tuning note: 0.5/0.5 was tried and reverted. Raising bm25_weight
        introduced cross-document keyword noise for definitional queries
        ("What is diabetes?") - other guideline PDFs (kidney disease,
        heart disease, asthma) mention "diabetes" repeatedly as a risk
        factor/comorbidity, so BM25's term-frequency scoring ranked
        those documents above the actual diabetes guideline once BM25's
        weight increased, even though vector search alone had correctly
        identified the diabetes PDF as most semantically relevant. Back
        to 0.4/0.6 (vector-leaning) - see evaluation results for before/
        after data justifying this in the report.
        reranker: optional CrossEncoderReranker instance (see reranker.py).
        When provided, search() fetches a wider shortlist from the
        BM25+vector stage, then hands it to the reranker for a final,
        more accurate pass - see the module docstring in reranker.py
        for why this two-stage design is used instead of relying on
        BM25/vector scores alone.

        use_mmr: when True, applies Maximal Marginal Relevance as a
        final diversification step (see _mmr_select() below) instead
        of just taking the top_k highest-scoring chunks outright.
        Motivation: relevance-only ranking (BM25/vector/rerank) can
        return several near-duplicate chunks from the same paragraph
        or section - e.g. 3 of the final 7 chunks all restating the
        same "high fever, headache" sentence with slightly different
        surrounding text - which wastes context budget that could have
        gone to a different, also-relevant fact elsewhere in the
        document (this was observed for "avoid"/precaution-style
        questions, where the single relevant fact can sit far from the
        highest-scoring symptom-description chunks). MMR trades a
        small amount of top-1 relevance for coverage of distinct
        information.
        mmr_lambda: relevance/diversity trade-off, 0-1. Higher = more
        weight on relevance (closer to plain top-k), lower = more
        weight on diversity. 0.7 favours relevance while still
        meaningfully penalizing near-duplicates.
        """
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.bm25_weight = bm25_weight
        self.vector_weight = vector_weight
        self.reranker = reranker
        self.use_mmr = use_mmr
        self.mmr_lambda = mmr_lambda
        self.bm25_index = None
        self.corpus_chunks = []  # list of {"id":..., "text":..., "metadata":...}

    def build_bm25_index(self, chunk_ids: List[str], texts: List[str],
                          metadatas: List[Dict[str, Any]] = None):
        """
        Build the BM25 index from all chunks.
        Must be called once after all chunks are added to the vector store.

        metadatas: optional list of {"source_document":..., "page_number":...}
        aligned with chunk_ids/texts - carried through so search results can
        cite exactly where each chunk came from.
        """
        if metadatas is None:
            metadatas = [{}] * len(chunk_ids)

        self.corpus_chunks = [
            {"id": cid, "text": text, "metadata": meta}
            for cid, text, meta in zip(chunk_ids, texts, metadatas)
        ]
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
            {
                "id": self.corpus_chunks[i]["id"],
                "text": self.corpus_chunks[i]["text"],
                "metadata": self.corpus_chunks[i].get("metadata", {}),
                "score": scores[i]
            }
            for i in range(len(scores))
        ]
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]

    def vector_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search using semantic vector similarity."""
        query_embedding = self.embedding_service.embed_text(query)
        results = self.vector_store.query(query_embedding, top_k=top_k)
        metadatas = results.get("metadatas", [[]])[0]

        scored_chunks = []
        for i, chunk_id in enumerate(results["ids"][0]):
            scored_chunks.append({
                "id": chunk_id,
                "text": results["documents"][0][i],
                "metadata": metadatas[i] if i < len(metadatas) else {},
                "score": 1 - results["distances"][0][i]  # convert distance to similarity
            })
        return scored_chunks

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Combine BM25 + vector search results using weighted scores.
        This is the main method other agents should call.

        If a reranker was provided in the constructor, this method casts
        a wider net first (top_k * 3 combined candidates instead of just
        top_k) and lets the cross-encoder pick the final top_k from that
        shortlist - this is what "optimized retrieval" means in practice:
        BM25+vector narrows millions of possible chunks down to a
        manageable shortlist fast, then the more accurate (but slower)
        cross-encoder makes the final call on just that shortlist.

        If use_mmr is also enabled, the reranked (or hybrid-scored, if
        no reranker) list is kept wider than top_k, and _mmr_select()
        picks the final top_k from it balancing relevance and diversity
        - see the use_mmr docstring in __init__ for why.
        """
        shortlist_k = top_k * 3 if (self.reranker or self.use_mmr) else top_k

        bm25_results = self.bm25_search(query, top_k=shortlist_k * 2)
        vector_results = self.vector_search(query, top_k=shortlist_k * 2)

        # normalize scores to 0-1 range within each method, then combine
        combined_scores = {}

        max_bm25 = max([r["score"] for r in bm25_results], default=1) or 1
        for r in bm25_results:
            normalized = r["score"] / max_bm25
            combined_scores[r["id"]] = {
                "text": r["text"],
                "metadata": r.get("metadata", {}),
                "score": normalized * self.bm25_weight
            }

        for r in vector_results:
            if r["id"] in combined_scores:
                combined_scores[r["id"]]["score"] += r["score"] * self.vector_weight
            else:
                combined_scores[r["id"]] = {
                    "text": r["text"],
                    "metadata": r.get("metadata", {}),
                    "score": r["score"] * self.vector_weight
                }

        combined_results = [
            {"id": cid, "text": data["text"], "metadata": data.get("metadata", {}), "score": data["score"]}
            for cid, data in combined_scores.items()
        ]
        combined_results.sort(key=lambda x: x["score"], reverse=True)
        shortlist = combined_results[:shortlist_k]

        # candidate_pool: the ranked list MMR/plain top-k will choose
        # the final top_k from. If reranking is on, that ranking (more
        # accurate than raw hybrid scores) is what MMR diversifies over.
        if self.reranker:
            # keep the pool wider than top_k so MMR has real choices to
            # diversify across; if MMR is off this just returns top_k.
            pool_size = shortlist_k if self.use_mmr else top_k
            candidate_pool = self.reranker.rerank(query, shortlist, top_k=pool_size)
        else:
            candidate_pool = shortlist

        if self.use_mmr:
            return self._mmr_select(query, candidate_pool, top_k=top_k)

        return candidate_pool[:top_k]

    def _mmr_select(self, query: str, candidates: List[Dict[str, Any]],
                     top_k: int) -> List[Dict[str, Any]]:
        """
        Maximal Marginal Relevance: greedily selects top_k candidates
        that balance relevance to the query against redundancy with
        chunks already selected.

        MMR(candidate) = lambda * relevance(candidate, query)
                          - (1 - lambda) * max_similarity(candidate, already_selected)

        Both relevance and inter-candidate similarity are computed as
        cosine similarity over embedding vectors from the same
        embedding_service used for vector search, so this stays
        consistent with how "similar" is defined elsewhere in the
        pipeline rather than introducing a second notion of similarity.
        """
        if len(candidates) <= top_k:
            return candidates

        texts = [c["text"] for c in candidates]
        query_vec = np.array(self.embedding_service.embed_text(query))
        candidate_vecs = np.array(self.embedding_service.embed_batch(texts))

        def cosine(a: np.ndarray, b: np.ndarray) -> float:
            denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1e-9
            return float(np.dot(a, b) / denom)

        relevance = [cosine(query_vec, v) for v in candidate_vecs]

        selected_idx = [int(np.argmax(relevance))]
        remaining_idx = [i for i in range(len(candidates)) if i not in selected_idx]

        while len(selected_idx) < top_k and remaining_idx:
            best_score, best_i = None, None
            for i in remaining_idx:
                max_sim_to_selected = max(
                    cosine(candidate_vecs[i], candidate_vecs[j]) for j in selected_idx
                )
                mmr_score = (
                    self.mmr_lambda * relevance[i]
                    - (1 - self.mmr_lambda) * max_sim_to_selected
                )
                if best_score is None or mmr_score > best_score:
                    best_score, best_i = mmr_score, i

            selected_idx.append(best_i)
            remaining_idx.remove(best_i)

        return [candidates[i] for i in selected_idx]


# Example usage (for testing this file individually)
if __name__ == "__main__":
    print("This module needs VectorStore and EmbeddingService instances to run.")
    print("Test it together with retriever_agent.py once other modules are ready.")