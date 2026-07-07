"""
vector_store.py
Member 2 - Retrieval & Vector Database

Purpose: Handles FAISS vector index setup, persistence, and add/query
operations. Uses FAISS instead of ChromaDB because ChromaDB's dependency
'chroma-hnswlib' requires a C++ compiler to build on Windows, which
caused installation issues. FAISS provides prebuilt wheels for Windows,
so no C++ compiler is needed.

This still satisfies the "Vector Persistence" requirement - the index
and its metadata are saved to disk and reloaded between sessions.
"""

import os
import pickle
from typing import List, Dict, Any
import numpy as np
import faiss  # pip install faiss-cpu


class VectorStore:
    """
    Wraps FAISS so the rest of the system interacts with a simple
    interface (add_chunks, query) instead of FAISS's raw API directly.

    Dependency Injection: persist_directory and collection_name are
    passed in, not hardcoded, so this class is reusable/testable.

    Note: FAISS only stores vectors + a numeric index. We keep the
    actual text/metadata ourselves in a Python dict, saved alongside
    the FAISS index file, so we can still return text + metadata
    when we query.
    """

    def __init__(self, persist_directory: str = "data/faiss_db",
                 collection_name: str = "medical_documents",
                 embedding_dim: int = 384):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_dim = embedding_dim

        os.makedirs(self.persist_directory, exist_ok=True)

        self.index_path = os.path.join(self.persist_directory, f"{collection_name}.index")
        self.metadata_path = os.path.join(self.persist_directory, f"{collection_name}_metadata.pkl")

        # id_map: maps FAISS's internal integer position -> our chunk data
        self.id_map: Dict[int, Dict[str, Any]] = {}

        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            # load existing index + metadata from disk (this is our "persistence")
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, "rb") as f:
                self.id_map = pickle.load(f)
            print(f"Loaded existing FAISS index with {self.index.ntotal} vectors.")
        else:
            # IndexFlatIP = exact search using inner product (works like cosine
            # similarity if embeddings are normalized, which sentence-transformers does)
            self.index = faiss.IndexFlatIP(self.embedding_dim)

    def _save(self):
        """Persist the FAISS index and metadata dict to disk."""
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.id_map, f)

    def add_chunks(self, chunk_ids: List[str], texts: List[str],
                   embeddings: List[List[float]], metadatas: List[Dict[str, Any]]):
        """
        Add chunks + their embeddings + metadata to the vector store.

        chunk_ids: unique id per chunk (e.g. "diabetes.pdf_chunk_0")
        texts: the actual chunk text (so we can retrieve it later)
        embeddings: vector embeddings from EmbeddingService
        metadatas: extra info like {"source_document": "diabetes.pdf"}
        """
        vectors = np.array(embeddings, dtype="float32")

        # normalize vectors so inner product = cosine similarity
        faiss.normalize_L2(vectors)

        start_position = self.index.ntotal
        self.index.add(vectors)

        for i, (cid, text, meta) in enumerate(zip(chunk_ids, texts, metadatas)):
            self.id_map[start_position + i] = {
                "id": cid,
                "text": text,
                "metadata": meta
            }

        self._save()
        print(f"Added {len(chunk_ids)} chunks to vector store.")

    def query(self, query_embedding: List[float], top_k: int = 5) -> Dict[str, Any]:
        """
        Query the vector store for the most similar chunks.
        Returns results in a ChromaDB-like format so the rest of the
        codebase (hybrid_search.py) doesn't need to change.
        """
        if self.index.ntotal == 0:
            return {"ids": [[]], "documents": [[]], "distances": [[]]}

        query_vector = np.array([query_embedding], dtype="float32")
        faiss.normalize_L2(query_vector)

        top_k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_vector, top_k)

        ids, documents, distances = [], [], []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            chunk_data = self.id_map[int(idx)]
            ids.append(chunk_data["id"])
            documents.append(chunk_data["text"])
            distances.append(1 - float(score))  # convert similarity to "distance"

        return {
            "ids": [ids],
            "documents": [documents],
            "distances": [distances]
        }

    def count(self) -> int:
        """Return how many chunks are currently stored (useful for testing)."""
        return self.index.ntotal

    def reset(self):
        """Delete all data (use carefully, mainly for testing)."""
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.id_map = {}
        self._save()


# Example usage (for testing this file individually)
if __name__ == "__main__":
    store = VectorStore(persist_directory="data/faiss_db_test")

    store.add_chunks(
        chunk_ids=["test_chunk_1"],
        texts=["Diabetes is a chronic disease."],
        embeddings=[[0.1] * 384],  # fake embedding for testing (all-MiniLM-L6-v2 = 384 dims)
        metadatas=[{"source_document": "test.pdf"}]
    )

    print(f"Total chunks stored: {store.count()}")