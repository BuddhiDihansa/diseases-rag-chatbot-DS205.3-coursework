"""
retriever_agent.py
Member 2 - Retrieval & Vector Database

Purpose: The Retrieval Agent used in the multi-agent pipeline.
This is what Member 3's agents will call to get relevant chunks.

FIXED VERSION: 
1. Now handles general questions properly - uses the original query
   or disease name instead of treating everything as symptoms.
2. Tags each chunk with its source document for traceability.
3. Added relevance threshold check.
"""

import os
import pickle
from typing import List, Dict, Any, Optional
from retrieval.embedding_service import EmbeddingService
from retrieval.vector_store import VectorStore
from retrieval.hybrid_search import HybridSearch


class RetrieverAgent:
    """
    The Retrieval Agent in the multi-agent architecture:

    User Query -> Symptom Agent -> [RetrieverAgent] -> Reasoning Agent -> Verification Agent

    This agent's only job: given a query, return the most relevant
    chunks of information from the vector store. It does NOT generate
    answers itself - that's the Reasoning Agent's job (Member 3).
    """

    def __init__(self, embedding_service: EmbeddingService = None,
                 vector_store: VectorStore = None,
                 hybrid_search: HybridSearch = None,
                 bm25_data_path: str = "data/bm25_data.pkl",
                 min_relevance_threshold: float = 0.1):
        """
        Dependency Injection: all dependencies passed in via constructor.
        This makes the agent easy to test (can inject mock/fake objects)
        and easy to swap implementations later.

        On startup, this automatically loads the BM25 index from the
        file saved by build_database.py, so you don't need to manually
        rebuild it every time the program runs.
        """
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or VectorStore()
        self.hybrid_search = hybrid_search or HybridSearch(
            vector_store=self.vector_store,
            embedding_service=self.embedding_service
        )
        self.min_relevance_threshold = min_relevance_threshold

        # auto-load BM25 index if build_database.py has already been run
        if os.path.exists(bm25_data_path):
            with open(bm25_data_path, "rb") as f:
                bm25_data = pickle.load(f)
            self.hybrid_search.build_bm25_index(bm25_data["chunk_ids"], bm25_data["texts"])
            print(f"[RetrieverAgent] Loaded BM25 index with {len(bm25_data['texts'])} chunks.")
        else:
            print("[RetrieverAgent] WARNING: No BM25 data found. Run build_database.py first.")

    def retrieve(self, query: str, top_k: int = 5, original_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Main method: takes a query, returns the top_k most relevant chunks.

        FIXED: If query is "NO_SYMPTOMS" or empty, uses original_query instead.

        Args:
            query: The search query (symptoms or disease name)
            top_k: Number of chunks to retrieve
            original_query: The user's full original question (fallback if query is invalid)

        Returns:
            List of retrieved chunks with metadata
        """
        # FIX: If query is "NO_SYMPTOMS" or empty, use original_query
        search_query = self._build_search_query(query, original_query)

        print(f"[RetrieverAgent] Searching for: '{search_query}'")
        results = self.hybrid_search.search(search_query, top_k=top_k)

        # Add source info to each result
        for r in results:
            if 'source' not in r:
                r['source'] = r.get('id', 'unknown').split('_')[0] if '_' in r.get('id', '') else 'unknown'

        print(f"[RetrieverAgent] Retrieved {len(results)} chunks:")
        for r in results:
            print(f"  - {r.get('id', 'unknown')} (source: {r.get('source', 'unknown')}, score: {r['score']:.3f})")

        return results

    def _build_search_query(self, query: str, original_query: Optional[str] = None) -> str:
        """
        Build the best search query based on available input.

        FIX: This is the key fix - handles "NO_SYMPTOMS" properly.
        """
        # If query is "NO_SYMPTOMS" or empty, use original_query
        if not query or query.upper() == "NO_SYMPTOMS":
            if original_query:
                return original_query
            return "medical information"

        # If query looks like a general question, use original_query
        question_patterns = ['what is', 'what are', 'how is', 'how does', 
                            'how to', 'when to', 'why is', 'why does']
        query_lower = query.lower()
        if any(pattern in query_lower for pattern in question_patterns):
            if original_query:
                return original_query

        return query

    def get_context_text(self, query: str, top_k: int = 8, original_query: Optional[str] = None) -> str:
        """
        Convenience method: returns retrieved chunks as a single
        combined text block, ready to feed into the LLM prompt.

        Each chunk is prefixed with its source document so the
        ReasoningAgent and VerificationAgent can trace claims back
        to a specific source (Traceability requirement).

        FIXED: Now passes original_query to retrieve() method.
        """
        results = self.retrieve(query, top_k=top_k, original_query=original_query)

        if not results:
            return ""

        # Check if results are relevant enough
        max_score = max([r.get('score', 0) for r in results]) if results else 0
        if max_score < self.min_relevance_threshold:
            print(f"[RetrieverAgent] WARNING: Max relevance score ({max_score:.3f}) below threshold ({self.min_relevance_threshold})")
            return ""

        context_parts = []
        for i, r in enumerate(results):
            source = r.get('source', 'unknown')
            score = r.get('score', 0)
            text = r.get('text', '')
            if text:
                context_parts.append(f"[Document {i+1}] [Source: {source}] [Relevance: {score:.3f}]\n{text}")

        return "\n\n".join(context_parts)

    def get_context_with_metadata(self, query: str, top_k: int = 8, original_query: Optional[str] = None) -> dict:
        """
        Returns both the context text and the raw results with metadata.
        Useful for debugging and for the ReasoningAgent to check relevance.
        """
        results = self.retrieve(query, top_k=top_k, original_query=original_query)
        context_text = self.get_context_text(query, top_k=top_k, original_query=original_query)

        max_score = max([r.get('score', 0) for r in results]) if results else 0

        return {
            "results": results,
            "context_text": context_text,
            "max_relevance_score": max_score,
            "is_relevant": max_score >= self.min_relevance_threshold,
            "num_results": len(results)
        }


# Example usage (for testing this file individually)
if __name__ == "__main__":
    agent = RetrieverAgent()

    # Test with symptom query
    print("=" * 60)
    print("TEST 1: Symptom query")
    context = agent.get_context_text(
        query="fever and joint pain and headache",
        original_query="I have fever and joint pain and headache"
    )
    print("\n--- Retrieved Context ---")
    print(context[:500] if context else "No context found")

    # Test with general question
    print("\n" + "=" * 60)
    print("TEST 2: General question")
    context = agent.get_context_text(
        query="NO_SYMPTOMS",
        original_query="What are the warning signs of a heart attack?"
    )
    print("\n--- Retrieved Context ---")
    print(context[:500] if context else "No context found")

    # Test with metadata
    print("\n" + "=" * 60)
    print("TEST 3: With metadata")
    result = agent.get_context_with_metadata(
        query="NO_SYMPTOMS",
        original_query="What are the warning signs of a heart attack?"
    )
    print(f"Max relevance score: {result['max_relevance_score']}")
    print(f"Is relevant: {result['is_relevant']}")
    print(f"Number of results: {result['num_results']}")