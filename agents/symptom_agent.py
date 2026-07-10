"""
symptom_agent.py
Member 3 - LLM/Agent Logic

Purpose: First agent in the pipeline. Takes the user's raw input
(natural language symptom description) and structures it into
a clean, searchable query for the Retrieval Agent.
"""

from agents.base_agent import BaseAgent
from services.llm_client import LLMClient


class SymptomAgent(BaseAgent):
    """
    User Query -> [SymptomAgent] -> Retrieval Agent -> Reasoning Agent -> Verification Agent

    Job: Extract and structure symptoms from free-text user input.
    E.g. "I have a headache and I feel really tired and hot" ->
         "headache, fatigue, fever"

    This structuring step improves retrieval accuracy - a clean list
    of symptoms matches disease documents better than raw conversational text.
    """

    def __init__(self, llm_client: LLMClient = None):
        super().__init__(name="SymptomAgent")
        self.llm_client = llm_client or LLMClient()

    def run(self, user_input: str) -> str:
        """
        Takes raw user text, returns a cleaned/structured symptom query.
        """
        self.log(f"Analyzing input: '{user_input}'")

        prompt = f"""You are a medical symptom extraction assistant.
Extract the key symptoms mentioned in the user's message below.
Return ONLY a comma-separated list of symptoms, nothing else.

User message: "{user_input}"

Symptoms:"""

        structured_symptoms = self.llm_client.generate(prompt)
        self.log(f"Extracted symptoms: {structured_symptoms}")

        return structured_symptoms.strip()


# Example usage (for testing this file individually)
if __name__ == "__main__":
    agent = SymptomAgent()
    result = agent.run("I have a really bad headache and I feel hot and tired all the time")
    print(f"\nFinal structured query: {result}")