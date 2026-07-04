"""Abstract base class for vector stores."""
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple


class BaseVectorStore(ABC):
    """Interface for all persistent vector store implementations."""

    @abstractmethod
    def add_documents(self, chunks: List[Dict]) -> None:
        """Embed and store a list of chunk dicts."""
        raise NotImplementedError

    @abstractmethod
    def query(self, query_text: str, n_results: int = 5) -> List[Dict]:
        """
        Retrieve the top-n most relevant chunks for a query.

        Returns:
            List of dicts with 'text', 'metadata', 'distance'.
        """
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """Delete all stored documents from the collection."""
        raise NotImplementedError
