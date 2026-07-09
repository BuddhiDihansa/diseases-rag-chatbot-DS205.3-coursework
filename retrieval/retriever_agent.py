"""
retriever_agent.py
Member 2 - Retrieval & Vector Database

Purpose: The Retrieval Agent used in the multi-agent pipeline.
This is what Member 3's agents will call to get relevant chunks.
"""

import os
import pickle
from typing import List, Dict, Any
from retrieval.embedding_service import EmbeddingService
from retrieval.vector_store import VectorStore
from retrieval.hybrid_search import HybridSearch
from retrieval.reranker import CrossEncoderReranker


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
                 use_reranker: bool = True):
        """
        Dependency Injection: all dependencies passed in via constructor.
        This makes the agent easy to test (can inject mock/fake objects)
        and easy to swap implementations later.

        use_reranker: when True (default), builds a CrossEncoderReranker
        and wires it into HybridSearch for a higher-precision second pass
        (see reranker.py for why). Set to False to skip loading the
        cross-encoder model - useful for quick tests where retrieval
        precision doesn't matter, since the cross-encoder model adds a
        few seconds of load time on startup.

        On startup, this automatically loads the BM25 index from the
        file saved by build_database.py, so you don't need to manually
        rebuild it every time the program runs.
        """
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or VectorStore()

        reranker = None
        if use_reranker and hybrid_search is None:
            try:
                reranker = CrossEncoderReranker()
            except Exception as e:
                # Fail gracefully: if the cross-encoder model can't be
                # downloaded/loaded (e.g. no internet on first run), fall
                # back to plain hybrid search instead of crashing the
                # whole system over an optional accuracy boost.
                print(f"[RetrieverAgent] WARNING: Could not load reranker ({e}). "
                      f"Continuing without re-ranking.")
                reranker = None

        self.hybrid_search = hybrid_search or HybridSearch(
            vector_store=self.vector_store,
            embedding_service=self.embedding_service,
            reranker=reranker
        )

        # auto-load BM25 index if build_database.py has already been run
        if os.path.exists(bm25_data_path):
            with open(bm25_data_path, "rb") as f:
                bm25_data = pickle.load(f)
            # metadatas key may be missing in older pickles built before this
            # traceability update - fall back gracefully instead of crashing.
            metadatas = bm25_data.get("metadatas")
            self.hybrid_search.build_bm25_index(bm25_data["chunk_ids"], bm25_data["texts"], metadatas)
            print(f"[RetrieverAgent] Loaded BM25 index with {len(bm25_data['texts'])} chunks.")
        else:
            print("[RetrieverAgent] WARNING: No BM25 data found. Run build_database.py first.")

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Main method: takes a query (e.g. symptoms description),
        returns the top_k most relevant chunks with their source info.

        This is what gets called in the pipeline (services/pipeline.py)
        and printed during the demo video to show "retrieved chunks".
        """
        print(f"[RetrieverAgent] Searching for: '{query}'")
        results = self.hybrid_search.search(query, top_k=top_k)

        print(f"[RetrieverAgent] Retrieved {len(results)} chunks:")
        for r in results:
            citation = self._format_citation(r.get("metadata", {}))
            print(f"  - {r['id']} (score: {r['score']:.3f}) [{citation}]")

        return results

    def get_context_text(self, query: str, top_k: int = 5) -> str:
        """
        Convenience method: returns retrieved chunks as a single
        combined text block, ready to feed into the LLM prompt.

        Each chunk is prefixed with a [Source: file.pdf, page N] tag so
        the LLM (and anyone reading the trace) can see exactly which
        document/page each piece of context came from - this is the
        "Traceability" requirement from the assessment brief.
        """
        results = self.retrieve(query, top_k=top_k)
        context_blocks = []
        for r in results:
            citation = self._format_citation(r.get("metadata", {}))
            context_blocks.append(f"[Source: {citation}]\n{r['text']}")
        return "\n\n".join(context_blocks)

    @staticmethod
    def _format_citation(metadata: Dict[str, Any]) -> str:
        """Builds a human-readable 'file.pdf, page 3' citation string from chunk metadata."""
        source = metadata.get("source_document", "unknown source")
        page = metadata.get("page_number")
        return f"{source}, page {page}" if page else source


# Example usage (for testing this file individually)
if __name__ == "__main__":
    agent = RetrieverAgent()
    context = agent.get_context_text("fever and joint pain and headache")
    print("\n--- Retrieved Context ---")
    print(context)