"""Abstract base class for LLM generation."""
from abc import ABC, abstractmethod
from typing import List, Dict


class BaseGenerator(ABC):
    """Interface for all LLM generator implementations."""

    @abstractmethod
    def generate(self, query: str, context: str) -> str:
        """Generate a grounded answer from the query and retrieved context."""
        raise NotImplementedError
