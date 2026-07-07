"""
embedding_service.py
Member 2 - Retrieval & Vector Database

Purpose: Wrapper class around the embedding model.
Converts text (chunks or queries) into vector embeddings.
"""

from typing import List
from sentence_transformers import SentenceTransformer  # pip install sentence-transformers


class EmbeddingService:
    """
    Wraps the embedding model so the rest of the system doesn't
    need to know which model is being used underneath.

    Dependency Injection: model_name is passed in via constructor,
    so it's easy to swap models later without changing other code.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        print(f"Loading embedding model: {model_name} ...")
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str) -> List[float]:
        """Embed a single piece of text (e.g. a user query)."""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple texts at once (e.g. all chunks from Member 1).
        Batch encoding is much faster than one-by-one.
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings.tolist()

    def get_embedding_dimension(self) -> int:
        """Return the dimension size of the embedding vectors (useful for ChromaDB setup)."""
        return self.model.get_sentence_embedding_dimension()


# Example usage (for testing this file individually)
if __name__ == "__main__":
    service = EmbeddingService()

    sample_texts = [
        "Diabetes is a chronic disease affecting insulin production.",
        "Asthma causes difficulty breathing due to airway inflammation."
    ]

    embeddings = service.embed_batch(sample_texts)
    print(f"Embedding dimension: {service.get_embedding_dimension()}")
    print(f"Number of embeddings created: {len(embeddings)}")