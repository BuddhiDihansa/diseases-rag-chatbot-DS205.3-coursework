"""
reasoning_agent.py
Member 3 - LLM/Agent Logic

Purpose:
Generate a grounded medical response using ONLY the retrieved context.
"""

from agents.base_agent import BaseAgent
from services.llm_client import LLMClient


class ReasoningAgent(BaseAgent):
    """
    User Query
        ↓
    SymptomAgent
        ↓
    RetrieverAgent
        ↓
    ReasoningAgent
        ↓
    VerificationAgent
    """

    def __init__(self, llm_client: LLMClient = None):
        super().__init__(name="ReasoningAgent")
        self.llm_client = llm_client or LLMClient()

    def run(
        self,
        symptoms: str,
        retrieved_context: str,
        feedback: str = None
    ) -> dict:
        """
        Generate a grounded answer using retrieved context only.

        Args:
            symptoms: Structured symptoms from SymptomAgent.
            retrieved_context: Retrieved chunks from RetrieverAgent.
            feedback: Optional verification feedback.

        Returns:
            dict
        """
        self.log("Generating grounded answer from retrieved context...")

        # Safety check
        if not retrieved_context or not retrieved_context.strip():
            self.log("No retrieved context available.")
            return {
                "symptoms_input": symptoms,
                "retrieved_context": "",
                "generated_answer":
                    "No relevant medical information was retrieved from the knowledge base.",
                "generation_failed": False
            }

        feedback_block = ""
        if feedback:
            feedback_block = f"""
IMPORTANT:
Your previous answer was rejected during verification.

Verification Feedback:
{feedback}

Correct the issues.
Use ONLY information explicitly supported by the retrieved context.
Do NOT invent new medical facts.
"""

        prompt = f"""
You are a medical Retrieval-Augmented Generation (RAG) assistant.

You MUST answer ONLY using the retrieved context.

Rules:
- Do NOT use outside medical knowledge.
- Do NOT guess.
- Do NOT invent diseases.
- Do NOT invent medications.
- Do NOT invent treatments.
- If the retrieved context is insufficient, clearly say so.
{feedback_block}
Retrieved Context:
{retrieved_context}

Patient Symptoms:
{symptoms}

Return EXACTLY in this format.

Possible Condition:
...

Confidence Note:
...

Recommended Actions:
- ...

Things to Avoid:
- ...
"""

        try:
            raw_response = self.llm_client.generate(prompt)
            self.log("Answer generated successfully.")
        except Exception as e:
            self.log(f"LLM generation failed: {e}")
            return {
                "symptoms_input": symptoms,
                "retrieved_context": retrieved_context,
                "generated_answer":
                    f"Error: Could not generate response. ({e})",
                # Explicit flag so downstream steps (VerificationAgent,
                # the pipeline) can tell "the LLM call itself failed"
                # apart from "the LLM generated a real answer" - without
                # this, an error string with no medical claims in it gets
                # judged 'faithful: Yes' by the verifier (nothing to
                # contradict) and gets shown to the user as a verified,
                # trustworthy answer, which it very much is not.
                "generation_failed": True
            }

        return {
            "symptoms_input": symptoms,
            "retrieved_context": retrieved_context,
            "generated_answer": raw_response,
            "generation_failed": False
        }


# --------------------------------------------------------
# Test this file independently
# --------------------------------------------------------
if __name__ == "__main__":
    agent = ReasoningAgent()

    fake_context = """
Dengue fever commonly presents with
high fever,
headache,
joint pain,
muscle pain,
and skin rash.

Patients should stay hydrated and seek medical attention
if warning signs develop.
"""

    result = agent.run(
        symptoms="fever, headache, joint pain",
        retrieved_context=fake_context
    )

    print("\n------ Generated Answer ------\n")
    print(result["generated_answer"])