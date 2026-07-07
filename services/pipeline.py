"""
pipeline.py
Shared (Member 2 + 3 coordinate on this) - services/pipeline.py

Purpose: The orchestrator. Connects all agents into a single flow.
This is what main.py calls - it hides the complexity of the
multi-agent chain behind one simple method: run(user_query).

Full flow:
User Query -> SymptomAgent -> RetrieverAgent -> ReasoningAgent -> VerificationAgent -> Final Answer

FIXED VERSION: previously the verification result was printed but never
acted on - a "No" or "Partially" verdict looked identical to a "Yes" to
the end user. This version checks final_output["needs_review"] (set by
the fixed VerificationAgent) and prints a clear warning block when the
answer could not be fully verified against the retrieved context.
"""

from agents.symptom_agent import SymptomAgent
from agents.reasoning_agent import ReasoningAgent
from agents.verification_agent import VerificationAgent
from retrieval.retriever_agent import RetrieverAgent
from services.llm_client import LLMClient


class MedicalAIPipeline:
    """
    Orchestrates the full multi-agent pipeline.

    Dependency Injection: all agents are passed in (or created with
    defaults) via the constructor. This means you can:
    - swap any agent for a test/mock version easily
    - test each agent independently
    - explain clearly in the Viva how the pieces connect
    """

    def __init__(self,
                 symptom_agent: SymptomAgent = None,
                 retriever_agent: RetrieverAgent = None,
                 reasoning_agent: ReasoningAgent = None,
                 verification_agent: VerificationAgent = None):

        # shared LLM client so we don't create multiple connections
        shared_llm_client = LLMClient()

        self.symptom_agent = symptom_agent or SymptomAgent(llm_client=shared_llm_client)
        self.retriever_agent = retriever_agent or RetrieverAgent()
        self.reasoning_agent = reasoning_agent or ReasoningAgent(llm_client=shared_llm_client)
        self.verification_agent = verification_agent or VerificationAgent(llm_client=shared_llm_client)

    def run(self, user_query: str, top_k: int = 5) -> dict:
        """
        Runs the full pipeline end-to-end for a single user query.

        Returns a dict with everything - useful for the demo video,
        since you can print each stage separately to show the
        "Ingestion -> Retrieval -> Synthesis -> Evaluation" trace.
        """
        print("=" * 60)
        print(f"USER QUERY: {user_query}")
        print("=" * 60)

        # Step 1: Symptom Agent - structure the raw input
        print("\n--- STEP 1: Symptom Analysis ---")
        structured_symptoms = self.symptom_agent.run(user_query)

        # Step 2: Retriever Agent - get relevant chunks from vector DB
        print("\n--- STEP 2: Retrieval ---")
        retrieved_context = self.retriever_agent.get_context_text(structured_symptoms, top_k=top_k)

        # Step 3: Reasoning Agent - generate grounded answer
        print("\n--- STEP 3: Reasoning / Answer Generation ---")
        reasoning_output = self.reasoning_agent.run(
            symptoms=structured_symptoms,
            retrieved_context=retrieved_context
        )

        # Step 4: Verification Agent - check for hallucinations
        print("\n--- STEP 4: Verification ---")
        final_output = self.verification_agent.run(reasoning_output)

        print("\n" + "=" * 60)
        print("FINAL ANSWER:")
        print(final_output["generated_answer"])

        verification = final_output["verification"]
        if final_output.get("needs_review"):
            print("\n[WARNING] This answer could not be fully verified against the source documents.")
            print(f"  Faithfulness: {verification['faithful']}")
            if verification["unsupported_claims"]:
                print("  Unsupported claims:")
                for claim in verification["unsupported_claims"]:
                    print(f"    - {claim}")
            print("  Treat this answer with extra caution.")
        else:
            print("\n[VERIFIED] This answer is grounded in the retrieved context.")

        print("=" * 60)

        return {
            "user_query": user_query,
            "structured_symptoms": structured_symptoms,
            "retrieved_context": retrieved_context,
            "generated_answer": final_output["generated_answer"],
            "verification": verification,
            "needs_review": final_output.get("needs_review", False)
        }


# Example usage (for testing this file individually)
if __name__ == "__main__":
    pipeline = MedicalAIPipeline()
    result = pipeline.run("I have a high fever, headache, and joint pain for the last 2 days")