"""
reasoning_agent.py
Member 3 - LLM/Agent Logic

Purpose:
Generate a grounded medical response using ONLY the retrieved context.
"""

from agents.base_agent import BaseAgent
from services.llm_client import LLMClient


class ReasoningAgent(BaseAgent):

    def __init__(self, llm_client: LLMClient = None):
        super().__init__(name="ReasoningAgent")
        self.llm_client = llm_client or LLMClient()

    def run(
        self,
        symptoms: str,
        retrieved_context: str,
        feedback: str = None,
        is_informational: bool = False,
    ) -> dict:

        self.log("Generating grounded answer from retrieved context...")

        if not retrieved_context or not retrieved_context.strip():
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

        # -----------------------------------------
        # INFORMATIONAL QUESTIONS
        # -----------------------------------------

        if is_informational:

            prompt = f"""
You are a medical Retrieval-Augmented Generation (RAG) assistant.

You MUST answer ONLY using the retrieved context.

Rules:

- Use ONLY information from the retrieved context.
- Do NOT use outside medical knowledge.
- Do NOT guess.
- Do NOT invent facts, drug names, treatments, statistics, or explanations.
- Answer ONLY what is asked.
- Maximum 3 sentences.
- Maximum 80 words.
- Do NOT repeat information.
- Do NOT add background information.
- Do NOT add examples unless explicitly present in the context.

Question-specific behavior:

- If symptoms are requested, return symptoms only.
- If causes are requested, return causes only.
- If treatments are requested, return treatments only.
- If precautions are requested, return precautions only.
- If a definition is requested, return a one-sentence definition.

If the answer is not present in the context, respond exactly:

"The retrieved context does not contain sufficient information."

{feedback_block}

Retrieved Context:
{retrieved_context}

Question:
{symptoms}

Short Answer:
"""

        # -----------------------------------------
        # SYMPTOM TRIAGE QUESTIONS
        # -----------------------------------------

        else:

            prompt = f"""
You are a medical Retrieval-Augmented Generation (RAG) assistant.

You MUST answer ONLY using the retrieved context.

Rules:

- Use ONLY information from the retrieved context.
- Do NOT use external medical knowledge.
- Keep responses concise.
- Avoid repetition.
- Maximum 2 sentences per section.
- Do NOT invent diagnoses.
- If information is uncertain, clearly state that.

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

            raw_response = self.llm_client.generate(
                prompt,
                max_tokens=120
            )

            raw_response = raw_response.strip()

            while "\n\n\n" in raw_response:
                raw_response = raw_response.replace(
                    "\n\n\n",
                    "\n\n"
                )

            self.log("Answer generated successfully.")

        except Exception as e:

            self.log(f"LLM generation failed: {e}")

            return {
                "symptoms_input": symptoms,
                "retrieved_context": retrieved_context,
                "generated_answer":
                    f"Error: Could not generate response. ({e})",
                "generation_failed": True
            }

        return {
            "symptoms_input": symptoms,
            "retrieved_context": retrieved_context,
            "generated_answer": raw_response,
            "generation_failed": False
        }


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
        symptoms="What are the symptoms of dengue fever?",
        retrieved_context=fake_context,
        is_informational=True
    )

    print("\n------ Generated Answer ------\n")
    print(result["generated_answer"])