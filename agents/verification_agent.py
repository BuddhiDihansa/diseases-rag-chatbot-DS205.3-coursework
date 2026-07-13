"""
verification_agent.py
Member 3 - LLM/Agent Logic

Purpose: Final agent in the pipeline. Checks whether the generated
answer is actually supported by the retrieved context (hallucination
check), and gives a confidence/faithfulness score.
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

        self.log("Verifying generated answer against retrieved context...")

        if reasoning_output.get("generation_failed"):
            self.log("Skipping verification - answer generation failed upstream.")
            verification = {
                "faithful": "No",
                "unsupported_claims": ["Answer generation failed - no response was produced to verify."]
            }
            reasoning_output["verification"] = verification
            reasoning_output["needs_review"] = True
            return reasoning_output

        prompt = f"""You are a medical fact checker reviewing an AI-generated answer.

Use ONLY the context below. Your job is to catch genuine hallucinations -
specific facts, numbers, drug names, or recommendations in the ANSWER
that are fabricated and NOT supported by the CONTEXT.

Context:
{context}

Answer:
{generated_answer}

Important - do NOT flag any of the following as unsupported, since they
are not hallucinations:
- Section labels or headers themselves (e.g. "Things to Avoid",
  "Confidence Note") - only flag the actual claim written under a
  header, never the header text.
- Reasonable paraphrasing, summarizing, or rewording of information
  that IS present in the context.
- General, cautious disclaimers such as "consult a healthcare
  professional" or "this is not a definitive diagnosis" - these are
  safe defaults, not factual claims that need grounding.
- Minor inferences that directly and obviously follow from the
  context (e.g. context says a drug treats X, answer says "this may
  help with X").

ONLY flag a claim if it introduces a specific fact, statistic, drug
name, dosage, or recommendation that cannot be traced back to
anything in the context.

Return ONLY a single valid JSON object, with no text before or after it,
in exactly this shape:
{{"faithful": "Yes", "unsupported_claims": []}}

Rules:
- "faithful" must be exactly one of: "Yes", "No", "Partially"
- "unsupported_claims" must be a JSON list of short strings (empty list if none)
- Do not include any explanation, markdown, or text outside the JSON object
"""

        raw_result = self.llm_client.generate(prompt)
        verification = self._parse_verification(raw_result)

        self.log(f"Verification result: {verification}")

        reasoning_output["verification"] = verification
        reasoning_output["needs_review"] = verification["faithful"] != "Yes"

        return reasoning_output

    def _parse_verification(self, raw_result: str) -> dict:
        """
        Safely parse the LLM's JSON response into a dict.

        LLMs sometimes wrap JSON in markdown code fences (```json ... ```)
        even when told not to, or add a stray sentence of preamble/
        postamble around the JSON object despite being told not to. Both
        are handled by extracting the substring between the first '{'
        and the last '}' rather than requiring the entire response to be
        pure JSON - this avoids treating a well-formed-but-decorated
        response as an unparseable one (which previously fell back to
        "Partially" and injected the parser's own error text - or even
        leaked prompt instructions - into unsupported_claims).

        If parsing still fails for any reason, we fall back to
        "Partially" (rather than silently assuming "Yes") so an
        unparseable response gets flagged for human review instead of
        passing through unnoticed.
        """
        if not raw_result:
            return {"faithful": "Partially", "unsupported_claims": ["Empty verification response"]}

        cleaned = raw_result.strip()

        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()

        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            cleaned = cleaned[start:end + 1]

        try:
            parsed = json.loads(cleaned)
            faithful = parsed.get("faithful", "Partially")
            unsupported_claims = parsed.get("unsupported_claims", [])

            if faithful not in ("Yes", "No", "Partially"):
                faithful = "Partially"
            if not isinstance(unsupported_claims, list):
                unsupported_claims = [str(unsupported_claims)]

            unsupported_claims = [
                c for c in unsupported_claims
                if c.strip().lower() not in ("things to avoid", "recommended actions", "confidence note", "possible condition")
            ]

            if not unsupported_claims and faithful != "Yes":
                faithful = "Yes"

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
        "generated_answer": "Possible Condition: Dengue Fever\nRecommended: rest and fluids."
    }
    result = agent.run(fake_reasoning_output)
    print("\n--- Verification Result ---")
    print(result["verification"])
    print("Needs review:", result["needs_review"])