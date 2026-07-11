"""
reasoning_agent.py
Member 3 - LLM/Agent Logic

Purpose: The core "Medical Reasoner" agent. Takes retrieved context
and the user's query, and generates a grounded answer using the LLM.

FIXED: Now checks if retrieved context is relevant before generating,
and explicitly tells the LLM to say "I don't know" if the context
doesn't contain the answer.
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

    def run(self, symptoms: str, retrieved_context: str, original_query: str = "") -> dict:
        """
        symptoms: structured symptom list from SymptomAgent
        retrieved_context: chunks of text from RetrieverAgent (Member 2)
        original_query: the user's full original question

        Returns a dict with the disease guess, dos, don'ts - kept structured
        so the Verification Agent can check it easily.
        """
        self.log("Generating grounded answer from retrieved context...")

        # Check if context is empty or too short
        if not retrieved_context or len(retrieved_context.strip()) < 50:
            self.log("WARNING: Retrieved context is empty or too short.")
            return self._create_unknown_response(
                symptoms,
                "No relevant medical documents were found."
            )

        # Determine what to use as the question in the prompt
        query_text = original_query if original_query else symptoms

        prompt = f"""
You are a medical RAG assistant.

You MUST answer ONLY using the retrieved context below.

CRITICAL RULES:
1. Do NOT use any outside medical knowledge, even if you are confident it is correct.
2. Do NOT guess or fill in gaps with plausible-sounding information.
3. Stay as close as possible to the exact wording, dosages, and figures given in the context.
4. Only say you don't have enough information if the context is completely unrelated to the question. If the context contains even partial relevant information, answer using what's there.
5. Answer the question directly and concisely in 1-3 plain sentences, the way a medical reference book would.
6. Do NOT use headers, labels, or bullet-point templates. Do NOT write "Possible Condition," "Confidence Note," "Recommended Actions," or "Things to Avoid." Just answer the question in plain prose.

Retrieved Context:
{retrieved_context}

User Question:
{query_text}

Answer:
"""

        raw_response = self.llm_client.generate(prompt, max_tokens=900)
        self.log("Answer generated.")

        return {
            "symptoms_input": symptoms,
            "retrieved_context": retrieved_context,
            "original_query": original_query,
            "generated_answer": raw_response,
            "is_confident": True
        }

    def _create_unknown_response(self, symptoms: str, reason: str) -> dict:
        """Create a response for when we don't have enough information."""
        return {
            "symptoms_input": symptoms,
            "retrieved_context": "",
            "original_query": "",
            "generated_answer": "I don't have enough information to answer this question. Please consult a healthcare provider.",
            "is_confident": False
        }


# Example usage (for testing this file individually)
if __name__ == "__main__":
    agent = ReasoningAgent()
    fake_context = "Dengue fever symptoms include high fever, headache, joint pain..."
    result = agent.run(
        symptoms="fever, headache, joint pain",
        retrieved_context=fake_context,
        original_query="What are the symptoms of dengue?"
    )
    print("\n--- Generated Answer ---")
    print(result["generated_answer"])