"""
test_agents.py
Tests for Member 3's agents module (base_agent, symptom_agent, reasoning_agent, verification_agent)

Run with: pytest tests/test_agents.py -v

Note: These tests use a FAKE/mock LLM client so they don't make real
API calls (faster, free, no API key needed for testing).
"""

import pytest
from agents.base_agent import BaseAgent
from agents.symptom_agent import SymptomAgent
from agents.reasoning_agent import ReasoningAgent
from agents.verification_agent import VerificationAgent


class FakeLLMClient:
    """
    A fake LLM client for testing - returns fixed responses instead
    of calling a real API. This is called 'mocking' - a common testing
    technique so tests are fast, free, and don't depend on the internet.
    """

    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        if "extract" in prompt.lower() or "symptom" in prompt.lower():
            return "fever, headache, joint pain"
        elif "faithful" in prompt.lower():
            return "Faithful: Yes\nUnsupported Claims: None"
        else:
            return "Possible Condition: Dengue Fever\nRecommended Actions (Do's): Rest and drink fluids."


class TestBaseAgent:

    def test_base_agent_is_abstract(self):
        # BaseAgent should not be instantiable directly since it's abstract
        with pytest.raises(TypeError):
            BaseAgent(name="test")


class TestSymptomAgent:

    def setup_method(self):
        self.agent = SymptomAgent(llm_client=FakeLLMClient())

    def test_run_returns_string(self):
        result = self.agent.run("I have a fever and my head hurts")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_agent_has_correct_name(self):
        assert self.agent.name == "SymptomAgent"


class TestReasoningAgent:

    def setup_method(self):
        self.agent = ReasoningAgent(llm_client=FakeLLMClient())

    def test_run_returns_dict_with_required_keys(self):
        result = self.agent.run(
            symptoms="fever, headache",
            retrieved_context="Dengue fever causes high fever and headache."
        )
        assert "generated_answer" in result
        assert "retrieved_context" in result
        assert "symptoms_input" in result


class TestVerificationAgent:

    def setup_method(self):
        self.agent = VerificationAgent(llm_client=FakeLLMClient())

    def test_run_adds_verification_field(self):
        fake_input = {
            "retrieved_context": "Dengue fever causes fever and headache.",
            "generated_answer": "Possible Condition: Dengue Fever"
        }
        result = self.agent.run(fake_input)
        assert "verification" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])