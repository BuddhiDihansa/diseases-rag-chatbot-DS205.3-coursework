"""Persistent ChromaDB vector store with sentence-transformer embeddings."""
import os
import uuid
from typing import List, Dict

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from app.vectorstore.base import BaseVectorStore


class ChromaVectorStore(BaseVectorStore):
    """
    Wraps ChromaDB with a SentenceTransformer embedding model.
    Data is persisted to disk so it survives between sessions.
    """

    def __init__(
        self,
        persist_directory: str,
        collection_name: str,
        embed_model_name: str = "all-MiniLM-L6-v2",
    ):
        """
        Args:
            persist_directory: Path where ChromaDB stores its files on disk.
            collection_name: Name of the ChromaDB collection.
            embed_model_name: HuggingFace sentence-transformer model name.
        """
        self.embed_model = SentenceTransformer(embed_model_name)

        # Persistent client — data survives between Streamlit reruns
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},  # cosine similarity for medical text
        )

    def add_documents(self, chunks: List[Dict]) -> None:
        """
        Embed all chunks and upsert into ChromaDB.

        Args:
            chunks: List of dicts with 'text' and 'metadata'.
        """
        if not chunks:
            return

        texts = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        ids = [str(uuid.uuid4()) for _ in chunks]

        # Batch embed for efficiency
        embeddings = self.embed_model.encode(texts, show_progress_bar=False).tolist()

        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )

    def query(self, query_text: str, n_results: int = 5) -> List[Dict]:
        """
        Embed the query and find the top-n similar chunks.

        Args:
            query_text: The user's symptom/question input.
            n_results: Number of chunks to retrieve.

        Returns:
            List of dicts: {'text': ..., 'metadata': ..., 'distance': ...}
        """
        query_embedding = self.embed_model.encode([query_text]).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        retrieved = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            retrieved.append({"text": doc, "metadata": meta, "distance": dist})

        return retrieved

    def clear(self) -> None:
        """Delete all documents in the collection."""
        self.collection.delete(where={"source": {"$ne": ""}})

    def count(self) -> int:
        """Return number of stored chunks."""
        return self.collection.count()
