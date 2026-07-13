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

        # Set by run() every time it's called. True when the last input
        # had no extractable symptoms (i.e. it was a general/informational
        # question like "What is diabetes?" rather than a symptom
        # narration). The pipeline reads this right after calling run()
        # to decide which ReasoningAgent prompt template to use - see
        # services/pipeline.py.
        self.last_is_informational: bool = False

    # Phrases the LLM sometimes returns instead of a clean empty string
    # when it means "no symptoms found". Treated the same as empty.
    _NO_SYMPTOM_PLACEHOLDERS = {
        "", "none", "n/a", "na", "no symptoms", "no symptoms found",
        "no symptoms mentioned", "zerowidthspace", "\u200b",
    }

    # Substrings that show up when the LLM explains itself instead of
    # returning a bare empty string/placeholder (e.g. "(No symptoms
    # were provided, only a general medical question about asthma, so
    # this is an empty string)"). The old exact-match check against
    # _NO_SYMPTOM_PLACEHOLDERS missed these entirely, which meant that
    # explanatory sentence itself got used as the retrieval search
    # query (garbage in, garbage out) AND last_is_informational stayed
    # False, so ReasoningAgent picked the wrong prompt template too.
    _NO_SYMPTOM_MARKERS = (
        "no symptom", "not describe", "not mention", "general question",
        "general medical question", "empty string", "does not provide",
        "no specific symptom",
    )

    # A real extracted symptom list is short ("fever, headache, joint
    # pain"). Anything this long is almost certainly the LLM explaining
    # itself in a full sentence rather than answering with a plain list,
    # regardless of whether it happens to contain a recognized marker
    # phrase - treated as a safety-net signal on top of the markers above.
    _MAX_PLAUSIBLE_SYMPTOM_WORDS = 12

    # If the user's message ITSELF is phrased as a general question about
    # a disease (starts with a question word and asks what to avoid/how
    # it's managed/etc.), it can never be a symptom narration - regardless
    # of what the LLM returns. This is a deterministic safety net on top
    # of the LLM classification above: temperature=0.0 reduces but does
    # not eliminate run-to-run variance on borderline cases (e.g. the LLM
    # occasionally inferring "fever" from the word "dengue" even though
    # the user never said they have a fever), and this question shape is
    # unambiguous enough to decide with a simple pattern match instead of
    # trusting the LLM every time.
    _INFORMATIONAL_QUESTION_MARKERS = (
        "what should", "what precautions", "what is", "what are",
        "how is", "how are", "how does", "how do", "when is", "when should",
        "can ", "does ", "is it", "should someone",
    )

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
          "N/A", a stray zero-width-space character, or (with the API's
          default sampling temperature) a full explanatory sentence.
          All of these are normalized and treated as "no symptoms
          found", and we fall back to the original question text as
          the retrieval query instead of searching with a useless/junk
          string, which previously caused the retriever to return
          near-random, irrelevant chunks for every such question.
        """
        self.log(f"Analyzing input: '{user_input}'")

        stripped_lower = user_input.strip().lower()
        if stripped_lower.startswith(self._INFORMATIONAL_QUESTION_MARKERS):
            self.log(
                "Input is phrased as a general question - skipping symptom "
                "extraction and using the original question as the "
                "retrieval query."
            )
            self.last_is_informational = True
            structured_symptoms = user_input.strip()
            self.log(f"Extracted symptoms: {structured_symptoms}")
            return structured_symptoms

        prompt = f"""You are a medical symptom extraction assistant.
Extract the key symptoms mentioned in the user's message below.
Return ONLY a comma-separated list of symptoms, nothing else - no
explanation, no full sentences, no preamble.
If the message does not describe any symptoms (e.g. it is a general
medical question like "What is diabetes?" or "How is X treated?"),
return ONLY an empty string and nothing else - do not return words
like "none" or "N/A", and do not explain why it's empty.

Example 1
User message: "I have a really bad headache and I feel hot"
Symptoms: headache, fever

Example 2
User message: "What are the symptoms of asthma?"
Symptoms:

Example 3
User message: "What are the warning signs of a heart attack?"
Symptoms:

Example 4
User message: "What should someone with dengue avoid?"
Symptoms:

Example 5
User message: "What precautions should a diabetic patient take with their diet?"
Symptoms:

IMPORTANT: Questions asking what to avoid, what precautions to take, how
a disease is managed/treated, or any other general question ABOUT a
disease are NOT symptom narrations - they are informational questions,
even if the disease name itself implies typical symptoms (e.g. "dengue"
implies fever). Do NOT infer or guess symptoms from the disease's name.
Only extract symptoms the user explicitly describes themselves
experiencing (e.g. "I have a fever and headache").

User message: "{user_input}"

Symptoms:"""

        raw_output = self.llm_client.generate(prompt).strip()

        # Normalize: strip invisible characters (e.g. zero-width space),
        # lowercase, and strip punctuation for the placeholder check.
        cleaned = raw_output.replace("\u200b", "").strip().strip(".").lower()

        looks_like_explanation = any(
            marker in cleaned for marker in self._NO_SYMPTOM_MARKERS
        )
        looks_too_long_for_a_symptom_list = (
            len(cleaned.split()) > self._MAX_PLAUSIBLE_SYMPTOM_WORDS
        )

        if (
            cleaned in self._NO_SYMPTOM_PLACEHOLDERS
            or looks_like_explanation
            or looks_too_long_for_a_symptom_list
        ):
            self.log(
                "No symptoms found in input - falling back to the original "
                "question as the retrieval query."
            )
            structured_symptoms = user_input.strip()
            self.last_is_informational = True
        else:
            structured_symptoms = raw_output
            self.last_is_informational = False

        self.log(f"Extracted symptoms: {structured_symptoms}")

        return structured_symptoms


# Example usage (for testing this file individually)
if __name__ == "__main__":
    agent = SymptomAgent()
    result = agent.run("I have a really bad headache and I feel hot and tired all the time")
    print(f"\nFinal structured query: {result}")