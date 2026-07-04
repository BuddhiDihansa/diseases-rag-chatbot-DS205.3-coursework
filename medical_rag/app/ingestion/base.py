"""Abstract base class for document ingestion."""
from abc import ABC, abstractmethod
from typing import List, Dict


class BaseIngester(ABC):
    """Abstract interface for all document ingesters."""

    @abstractmethod
    def load(self, source: str) -> List[Dict]:
        """
        Load a document from source and return a list of chunk dicts.
        Each dict must have keys: 'text', 'metadata'.
        """
        raise NotImplementedError

    @abstractmethod
    def chunk(self, text: str, metadata: Dict) -> List[Dict]:
        """Split a full document text into overlapping chunks."""
        raise NotImplementedError
