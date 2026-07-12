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
    """

    def __init__(self, llm_client: LLMClient = None):
        super().__init__(name="SymptomAgent")
        self.llm_client = llm_client or LLMClient()

    # Phrases the LLM sometimes returns instead of a clean empty string
    # when it means "no symptoms found". Treated the same as empty.
    _NO_SYMPTOM_PLACEHOLDERS = {
        "", "none", "n/a", "na", "no symptoms", "no symptoms found",
        "no symptoms mentioned", "zerowidthspace", "\u200b",
    }

    def run(self, user_input: str) -> str:
        """
        Takes raw user text, returns a cleaned/structured symptom query.

        Handles two kinds of input:
        - Symptom narrations ("I have a headache and fever") -> extracts
          a clean comma-separated symptom list.
        - General medical/informational questions ("What is diabetes?",
          "How is hypertension managed?") -> there are no symptoms to
          extract. The LLM is inconsistent about how it signals this -
          sometimes an empty string, sometimes the literal word "none",
          "N/A", or a stray zero-width-space character. All of these
          are normalized and treated as "no symptoms found", and we
          fall back to the original question text as the retrieval
          query instead of searching with a useless/junk string, which
          previously caused the retriever to return near-random,
          irrelevant chunks for every such question.
        """
        self.log(f"Analyzing input: '{user_input}'")

        prompt = f"""You are a medical symptom extraction assistant.
Extract the key symptoms mentioned in the user's message below.
Return ONLY a comma-separated list of symptoms, nothing else.
If the message does not describe any symptoms (e.g. it is a general
medical question like "What is diabetes?" or "How is X treated?"),
return an empty string - do not return words like "none" or "N/A".

User message: "{user_input}"

Symptoms:"""

        raw_output = self.llm_client.generate(prompt).strip()

        # Normalize: strip invisible characters (e.g. zero-width space),
        # lowercase, and strip punctuation for the placeholder check.
        cleaned = raw_output.replace("\u200b", "").strip().strip(".").lower()

        if cleaned in self._NO_SYMPTOM_PLACEHOLDERS:
            self.log(
                "No symptoms found in input - falling back to the original "
                "question as the retrieval query."
            )
            structured_symptoms = user_input.strip()
        else:
            structured_symptoms = raw_output

        self.log(f"Extracted symptoms: {structured_symptoms}")

        return structured_symptoms


# Example usage (for testing this file individually)
if __name__ == "__main__":
    agent = SymptomAgent()
    result = agent.run("I have a really bad headache and I feel hot and tired all the time")
    print(f"\nFinal structured query: {result}")