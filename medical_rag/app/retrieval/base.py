"""Abstract base class for retrieval."""
from abc import ABC, abstractmethod
from typing import List, Dict


class BaseRetriever(ABC):
    """Interface for all retrieval strategies."""

    @abstractmethod
    def retrieve(self, query: str, n_results: int = 5) -> List[Dict]:
        """Retrieve relevant chunks for a query. Returns list of chunk dicts."""
        raise NotImplementedError

    @abstractmethod
    def format_context(self, chunks: List[Dict]) -> str:
        """Format retrieved chunks into a context string for the LLM prompt."""
        raise NotImplementedError
