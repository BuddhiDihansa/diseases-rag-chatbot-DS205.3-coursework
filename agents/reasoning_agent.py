"""
reasoning_agent.py
Member 3 - LLM/Agent Logic

Purpose: The core "Medical Reasoner" agent. Takes retrieved context
(from Member 2's RetrieverAgent) + the user's symptoms, and generates
a grounded answer using the LLM.
"""

from agents.base_agent import BaseAgent
from services.llm_client import LLMClient


class ReasoningAgent(BaseAgent):
    """
    User Query -> Symptom Agent -> Retrieval Agent -> [ReasoningAgent] -> Verification Agent

    Job: Generate the final answer using ONLY the retrieved context
    (grounded generation). This is what makes it a RAG system rather
    than a plain LLM chatbot - the answer must be traceable back to
    the source documents.
    """

    def __init__(self, llm_client: LLMClient = None):
        super().__init__(name="ReasoningAgent")
        self.llm_client = llm_client or LLMClient()

    def run(self, symptoms: str, retrieved_context: str) -> dict:
        """
        symptoms: structured symptom list from SymptomAgent
        retrieved_context: chunks of text from RetrieverAgent (Member 2)

        Returns a dict with the disease guess, dos, don'ts - kept structured
        so the Verification Agent can check it easily.
        """
        self.log("Generating grounded answer from retrieved context...")
        
        print(repr(retrieved_context))

        prompt = f"""
You are a medical RAG assistant.

You MUST answer ONLY using the retrieved context below.

Rules:
- Do NOT use any outside medical knowledge.
- Do NOT guess.
- Do NOT invent diseases, treatments, or medications.
- If the context does not explicitly support a diagnosis, write:
  "Possible Condition: Not enough information in the provided medical documents."
- Every recommendation must come directly from the context.

Retrieved Context:
{retrieved_context}

Patient Symptoms:
{symptoms}

Return exactly in this format:

Possible Condition:
...

Confidence Note:
...

Recommended Actions:
- ...

Things to Avoid:
- ...
"""

        raw_response = self.llm_client.generate(prompt)
        self.log("Answer generated.")

        return {
            "symptoms_input": symptoms,
            "retrieved_context": retrieved_context,
            "generated_answer": raw_response
        }


# Example usage (for testing this file individually)
if __name__ == "__main__":
    agent = ReasoningAgent()
    fake_context = "Dengue fever symptoms include high fever, headache, joint pain..."
    result = agent.run(symptoms="fever, headache, joint pain", retrieved_context=fake_context)
    print("\n--- Generated Answer ---")
    print(result["generated_answer"])