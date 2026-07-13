"""
exceptions.py
Shared custom exceptions for the project.

Purpose: Instead of raising generic Exception everywhere, we define
specific exception types so calling code can catch/handle different
failure modes differently (e.g. a config error vs an API failure).
"""


class ConfigurationError(Exception):
    """Raised when required configuration (e.g. API key) is missing or invalid."""
    pass


class LLMGenerationError(Exception):
    """Raised when the LLM API call fails after all retries are exhausted."""
    pass