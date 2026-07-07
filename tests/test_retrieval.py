"""
test_retrieval.py
Tests for Member 2's retrieval module (embedding_service, vector_store, hybrid_search)

Run with: pytest tests/test_retrieval.py -v

Note: These tests use a temporary/test ChromaDB directory so they
don't interfere with your real vector database.
"""

import pytest
import shutil
import os
from retrieval.embedding_service import EmbeddingService
from retrieval.vector_store import VectorStore


TEST_DB_DIR = "data/chroma_db_test"


class TestEmbeddingService:

    def setup_method(self):
        self.service = EmbeddingService()

    def test_embed_text_returns_vector(self):
        embedding = self.service.embed_text("fever and headache")
        assert isinstance(embedding, list)
        assert len(embedding) > 0

    def test_embed_batch_returns_correct_count(self):
        texts = ["diabetes symptoms", "asthma treatment", "dengue fever"]
        embeddings = self.service.embed_batch(texts)
        assert len(embeddings) == len(texts)

    def test_similar_texts_have_similar_embeddings(self):
        import numpy as np
        emb1 = self.service.embed_text("high fever and headache")
        emb2 = self.service.embed_text("fever with headache")
        emb3 = self.service.embed_text("recipe for chocolate cake")

        # cosine similarity - similar texts should be closer than unrelated ones
        def cosine_sim(a, b):
            a, b = np.array(a), np.array(b)
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        sim_related = cosine_sim(emb1, emb2)
        sim_unrelated = cosine_sim(emb1, emb3)
        assert sim_related > sim_unrelated


class TestVectorStore:

    def setup_method(self):
        self.store = VectorStore(persist_directory=TEST_DB_DIR, collection_name="test_collection")

    def teardown_method(self):
        # clean up test database after each test
        if os.path.exists(TEST_DB_DIR):
            shutil.rmtree(TEST_DB_DIR)

    def test_add_and_count_chunks(self):
        self.store.add_chunks(
            chunk_ids=["chunk_1", "chunk_2"],
            texts=["Diabetes info", "Asthma info"],
            embeddings=[[0.1] * 384, [0.2] * 384],
            metadatas=[{"source": "test1.pdf"}, {"source": "test2.pdf"}]
        )
        assert self.store.count() == 2

    def test_query_returns_results(self):
        self.store.add_chunks(
            chunk_ids=["chunk_1"],
            texts=["Diabetes causes high blood sugar."],
            embeddings=[[0.1] * 384],
            metadatas=[{"source": "test1.pdf"}]
        )
        results = self.store.query(query_embedding=[0.1] * 384, top_k=1)
        assert len(results["ids"][0]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])