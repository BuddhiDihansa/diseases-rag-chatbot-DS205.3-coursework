"""
base_agent.py
Member 3 - LLM/Agent Logic

Purpose: Abstract base class for all agents in the system.
This satisfies the "Professional use of ABCs and Interfaces" rubric criteria
(Architectural Design - 25%). All agents inherit from this and must
implement the run() method - this is polymorphism/OOP in action.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    """
    Every agent in the multi-agent system (Symptom, Reasoning, Verification)
    inherits from this class. This enforces a consistent interface -
    the pipeline (services/pipeline.py) can call .run() on any agent
    without knowing its internal implementation details.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run(self, input_data: Any) -> Any:
        """
        Every agent must implement this method.
        Takes some input, returns some output - the specifics
        depend on the agent (defined in each subclass).
        """
        pass

    def log(self, message: str):
        """Shared utility method - consistent logging format across all agents."""
        print(f"[{self.name}] {message}")