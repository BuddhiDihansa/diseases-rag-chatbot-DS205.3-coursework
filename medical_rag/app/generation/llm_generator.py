"""LLM answer generation via Groq API (llama-3.3-70b-versatile)."""
import os
from groq import Groq
from app.generation.base import BaseGenerator


SYSTEM_PROMPT = """You are a medical information assistant. Your ONLY job is to answer 
questions based on the provided medical documents. 

STRICT RULES:
1. Only use information explicitly stated in the [CONTEXT] section.
2. If the context does not contain enough information, say: "I could not find 
   sufficient information about this in the provided medical documents."
3. Never make up symptoms, diagnoses, or treatments.
4. Always cite which source/page your answer came from.
5. Add a disclaimer: "This is for informational purposes only. Consult a doctor."

Your answer must be grounded, traceable, and faithful to the source documents."""


class GroqGenerator(BaseGenerator):
    """
    Generates grounded medical answers using the Groq LLM API.
    Uses a strict system prompt to minimize hallucination.
    """

    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        """
        Args:
            model: Groq model identifier.
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set in environment variables.")
        self.client = Groq(api_key=api_key)
        self.model = model

    def generate(self, query: str, context: str) -> str:
        """
        Send the query + retrieved context to the LLM and return the answer.

        AGENTIC LOOP STEP: This is the 'synthesis' step — the LLM sees only
        the retrieved context, not the full PDF. This grounds every response.

        Args:
            query: The user's original question or symptom description.
            context: Pre-formatted string of retrieved document chunks.

        Returns:
            The LLM's grounded, cited answer string.
        """
        user_message = f"""[CONTEXT]
{context}

[QUESTION]
{query}

Answer based strictly on the context above. Cite source numbers."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.1,   # Low temperature = more factual, less creative
            max_tokens=1024,
        )

        return response.choices[0].message.content
