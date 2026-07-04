"""Retriever with full traceability — shows what was retrieved vs generated."""
from typing import List, Dict
from app.retrieval.base import BaseRetriever
from app.vectorstore.base import BaseVectorStore


class MedicalRetriever(BaseRetriever):
    """
    Retrieves relevant medical document chunks and formats them for the LLM.
    Supports full traceability by exposing raw retrieved chunks.
    """

    def __init__(self, vector_store: BaseVectorStore):
        """
        Dependency Injection: accepts any BaseVectorStore implementation.

        Args:
            vector_store: A persistent vector store instance.
        """
        self.vector_store = vector_store

    def retrieve(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Query the vector store and return raw retrieved chunks.

        TRACEABILITY: The caller can inspect exactly what the system
        retrieved before the LLM generates any response.

        Args:
            query: User's symptom description or question.
            n_results: Number of chunks to retrieve.

        Returns:
            List of chunk dicts with text, metadata, and similarity distance.
        """
        chunks = self.vector_store.query(query_text=query, n_results=n_results)
        return chunks

    def format_context(self, chunks: List[Dict]) -> str:
        """
        Format retrieved chunks into a numbered context block for the LLM prompt.

        Args:
            chunks: List of retrieved chunk dicts.

        Returns:
            Formatted string context.
        """
        if not chunks:
            return "No relevant medical information found in the knowledge base."

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk["metadata"].get("source", "Unknown")
            page = chunk["metadata"].get("page", "?")
            context_parts.append(
                f"[Source {i}: {source}, Page {page}]\n{chunk['text']}"
            )

        return "\n\n---\n\n".join(context_parts)
