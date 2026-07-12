"""
pipeline.py
Shared (Member 2 + 3 coordinate on this) - services/pipeline.py

Purpose: The orchestrator. Connects all agents into a single flow.
This is what main.py calls - it hides the complexity of the
multi-agent chain behind one simple method: run(user_query).

Full flow (with self-correction):
User Query -> SymptomAgent -> RetrieverAgent -> ReasoningAgent -> VerificationAgent
                                                       ^                  |
                                                       |__ retry w/ ______|
                                                           feedback if
                                                           not faithful

This is the "Agentic Loop" the assessment brief asks for: the pipeline
isn't a single one-way pass. If VerificationAgent finds the answer
isn't fully supported by the retrieved context, the pipeline retries
ReasoningAgent with explicit feedback about what was wrong (up to
max_reflection_attempts times) before falling back to surfacing a
clearly-labelled "needs review" answer to the user.
"""

import time

from agents.symptom_agent import SymptomAgent
from agents.reasoning_agent import ReasoningAgent
from agents.verification_agent import VerificationAgent
from retrieval.retriever_agent import RetrieverAgent
from services.llm_client import LLMClient
from utils.logger import get_logger

logger = get_logger("MedicalAIPipeline")


class MedicalAIPipeline:
    """
    Orchestrates the full multi-agent pipeline.

    Dependency Injection: all agents are passed in (or created with
    defaults) via the constructor.
    """

    def __init__(
        self,
        symptom_agent: SymptomAgent = None,
        retriever_agent: RetrieverAgent = None,
        reasoning_agent: ReasoningAgent = None,
        verification_agent: VerificationAgent = None,
        max_reflection_attempts: int = 2,
    ):
        """
        max_reflection_attempts: how many times ReasoningAgent will retry
        generating an answer if VerificationAgent flags it as not fully
        faithful to the retrieved context.
        """

        # Shared LLM client
        shared_llm_client = LLMClient()

        self.symptom_agent = symptom_agent or SymptomAgent(
            llm_client=shared_llm_client
        )
        self.retriever_agent = retriever_agent or RetrieverAgent(
            llm_client=shared_llm_client
        )
        self.reasoning_agent = reasoning_agent or ReasoningAgent(
            llm_client=shared_llm_client
        )
        self.verification_agent = verification_agent or VerificationAgent(
            llm_client=shared_llm_client
        )
        self.max_reflection_attempts = max_reflection_attempts

    def run(self, user_query: str, top_k: int = 7) -> dict:
        """
        Runs the full pipeline end-to-end for a single user query,
        with a self-correction (reflection) loop around
        Reasoning + Verification.
        """

        print("=" * 60)
        print(f"USER QUERY: {user_query}")
        print("=" * 60)

        # Step 1
        print("\n--- STEP 1: Symptom Analysis ---")
        structured_symptoms = self.symptom_agent.run(user_query)

        # SymptomAgent sets this flag during run() above: True when the
        # query had no extractable symptoms (a general/informational
        # question rather than a symptom narration). Used below to widen
        # retrieval and to pick the right ReasoningAgent prompt template.
        is_informational = self.symptom_agent.last_is_informational

        # Step 2
        print("\n--- STEP 2: Retrieval ---")
        # top_k default raised from 5 to 7 (see run() signature above).
        # Evaluation showed some correct facts sat just outside the
        # top-5 cutoff by a small margin (e.g. the primary Dengue
        # symptom list scored close behind the top 5 chunks that were
        # being returned) - 7 catches those borderline-relevant chunks.
        # A larger jump (top_k*2 = 10) was tried earlier and reverted:
        # it let unrelated documents that merely *mention* the topic in
        # passing (e.g. "diabetes" referenced inside the kidney-disease
        # guideline) crowd out the actually-relevant document for
        # definitional queries. 7 is a smaller, safer step in the same
        # direction.
        #
        # expand_query=is_informational: query expansion (see
        # retrieval/query_expander.py) is enabled only for
        # informational questions, not symptom-triage ones. Symptom
        # narrations ("fever, joint pain, rash") already match clinical
        # text well via vector search since they use the same
        # vocabulary the guidelines do. Informational questions phrased
        # in layperson terms ("what should someone with dengue avoid?")
        # are the ones that suffer from vocabulary mismatch against
        # formal guideline language ("contraindicated", "NSAID") - that
        # is where multi-query retrieval earns its extra LLM call.
        retrieved_context = self.retriever_agent.get_context_text(
            structured_symptoms,
            top_k=top_k,
            expand_query=is_informational,
        )

        # Steps 3 + 4
        feedback = None
        final_output = None

        for attempt in range(1, self.max_reflection_attempts + 1):

            print(
                f"\n--- STEP 3: Reasoning / Answer Generation (attempt {attempt}) ---"
            )

            reasoning_output = self.reasoning_agent.run(
                symptoms=structured_symptoms,
                retrieved_context=retrieved_context,
                feedback=feedback,
                is_informational=is_informational,
            )

            print(
                f"\n--- STEP 4: Verification (attempt {attempt}) ---"
            )

            final_output = self.verification_agent.run(reasoning_output)

            if not final_output.get("needs_review"):
                logger.info(
                    f"Answer verified as faithful on attempt {attempt}."
                )
                break

            verification = final_output["verification"]

            logger.warning(
                f"Attempt {attempt} flagged as not fully faithful "
                f"(faithful={verification['faithful']}). "
                f"Unsupported claims: {verification['unsupported_claims']}"
            )

            if attempt < self.max_reflection_attempts:
                unsupported = verification.get("unsupported_claims") or []

                feedback = (
                    f"the answer was judged "
                    f"'{verification['faithful']}' faithful, "
                    f"with these unsupported claims: "
                    f"{', '.join(unsupported) if unsupported else 'unspecified'}"
                )

                print(f"\n[REFLECTION] Retrying with feedback: {feedback}")
                time.sleep(2)

        print("\n" + "=" * 60)
        print("FINAL ANSWER:")
        print(final_output["generated_answer"])

        verification = final_output["verification"]

        if final_output.get("needs_review"):
            print(
                f"\n[WARNING] This answer could not be fully verified "
                f"against the source documents after "
                f"{self.max_reflection_attempts} attempt(s)."
            )
            print(f"Faithfulness: {verification['faithful']}")

            if verification["unsupported_claims"]:
                print("Unsupported claims:")
                for claim in verification["unsupported_claims"]:
                    print(f" - {claim}")

            print("Treat this answer with extra caution.")

        else:
            print("\n[VERIFIED] This answer is grounded in the retrieved context.")

        print("=" * 60)

        return {
            "user_query": user_query,
            "structured_symptoms": structured_symptoms,
            "retrieved_context": retrieved_context,
            "generated_answer": final_output["generated_answer"],
            "verification": verification,
            "needs_review": final_output.get("needs_review", False),
        }


if __name__ == "__main__":
    pipeline = MedicalAIPipeline()
    result = pipeline.run(
        "I have a high fever, headache, and joint pain for the last 2 days"
    )