"""
verification_agent.py
Member 3 - LLM/Agent Logic

Purpose: Final agent in the pipeline. Checks whether the generated
answer is actually supported by the retrieved context (hallucination
check), and gives a confidence/faithfulness score.

FIXED: Now handles "I don't know" responses properly and doesn't
flag them as hallucinations.
"""

import json
from agents.base_agent import BaseAgent
from services.llm_client import LLMClient


class VerificationAgent(BaseAgent):
    """
    User Query -> Symptom Agent -> Retrieval Agent -> Reasoning Agent -> [VerificationAgent] -> Final Answer

    Job: Compare the generated answer against the retrieved context.
    Flag any claims that are NOT supported by the context (hallucinations).
    """

    def __init__(self, llm_client: LLMClient = None):
        super().__init__(name="VerificationAgent")
        self.llm_client = llm_client or LLMClient()

    def run(self, reasoning_output: dict) -> dict:
        """
        reasoning_output: the dict returned by ReasoningAgent.run()
        (contains generated_answer + retrieved_context)

        Returns the same dict, with added fields:
          - "verification": {"faithful": "Yes"/"No"/"Partially", "unsupported_claims": [...]}
          - "needs_review": True if faithful != "Yes" (use this to warn the user)
        """
        generated_answer = reasoning_output["generated_answer"]
        context = reasoning_output["retrieved_context"]
        is_confident = reasoning_output.get("is_confident", True)

        self.log("Verifying generated answer against retrieved context...")

        # If the answer is an "I don't know" response, mark as faithful
        if not is_confident or "I don't have enough information" in generated_answer:
            self.log("Answer is an 'I don't know' response - marking as faithful.")
            reasoning_output["verification"] = {
                "faithful": "Yes",
                "unsupported_claims": [],
                "note": "Answer appropriately indicates lack of information."
            }
            reasoning_output["needs_review"] = False
            return reasoning_output

        # If context is empty or very short
        if not context or len(context.strip()) < 50:
            self.log("WARNING: Context is empty or too short.")
            reasoning_output["verification"] = {
                "faithful": "No",
                "unsupported_claims": ["Context is empty or insufficient for verification."],
                "note": "No source documents available to verify the answer."
            }
            reasoning_output["needs_review"] = True
            return reasoning_output

        prompt = f"""You are a strict medical fact checker.

Use ONLY the context below. Check whether every claim in the ANSWER is
explicitly supported by the CONTEXT.

Context:
{context}

Answer:
{generated_answer}

Return ONLY a single valid JSON object, with no text before or after it,
in exactly this shape:
{{"faithful": "Yes", "unsupported_claims": []}}

Rules:
- "faithful" must be exactly one of: "Yes", "No", "Partially"
- "unsupported_claims" must be a JSON list of short strings (empty list if none)
- Do not include any explanation, markdown, or text outside the JSON object
"""

        raw_result = self.llm_client.generate(prompt, max_tokens=150)
        verification = self._parse_verification(raw_result)

        self.log(f"Verification result: {verification}")

        reasoning_output["verification"] = verification
        reasoning_output["needs_review"] = verification["faithful"] != "Yes"

        return reasoning_output

    def _parse_verification(self, raw_result: str) -> dict:
        """
        Safely parse the LLM's JSON response into a dict.
        """
        if not raw_result:
            return {"faithful": "Partially", "unsupported_claims": ["Empty verification response"]}

        cleaned = raw_result.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()

        try:
            parsed = json.loads(cleaned)
            faithful = parsed.get("faithful", "Partially")
            unsupported_claims = parsed.get("unsupported_claims", [])

            if faithful not in ("Yes", "No", "Partially"):
                faithful = "Partially"
            if not isinstance(unsupported_claims, list):
                unsupported_claims = [str(unsupported_claims)]

            return {"faithful": faithful, "unsupported_claims": unsupported_claims}

        except (json.JSONDecodeError, AttributeError, TypeError):
            return {
                "faithful": "Partially",
                "unsupported_claims": [f"Could not parse verification response: {cleaned[:100]}"]
            }


# Example usage (for testing this file individually)
if __name__ == "__main__":
    agent = VerificationAgent()
    fake_reasoning_output = {
        "retrieved_context": "Dengue fever symptoms include high fever, headache, joint pain.",
        "generated_answer": "Possible Condition: Dengue Fever\nRecommended: rest and fluids.",
        "is_confident": True
    }
    result = agent.run(fake_reasoning_output)
    print("\n--- Verification Result ---")
    print(result["verification"])
    print("Needs review:", result["needs_review"])