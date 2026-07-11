"""
symptom_agent.py
Member 1 - Symptom Analysis Agent

FIXED (v2): Reordered priority so that an explicit disease name
mentioned in the query is checked FIRST, before attempting generic
LLM symptom extraction. Previously, LLM symptom extraction ran first
and would happily invent plausible-sounding generic symptoms for
questions like "What are the symptoms of chikungunya?" (e.g. "fever,
joint pain, rash...") instead of admitting it didn't know - which
meant the disease-keyword check never ran, and the vague generic
symptom list retrieved weaker, less relevant, mixed-source chunks
instead of the disease's actual dedicated section in the source PDF.

Also expanded DISEASE_KEYWORDS to include several diseases that were
previously missing (chikungunya, migraine, nephrotic syndrome, status
epilepticus, snake bite, diabetic ketoacidosis, tension headache,
cluster headache) - these were silently falling through to weaker
symptom-based search before.
"""

from agents.base_agent import BaseAgent
from services.llm_client import LLMClient

# Disease keywords for general questions - checked FIRST, before LLM
# symptom extraction, since an explicit disease name is a much more
# precise and reliable search term than inferred/generic symptoms.
DISEASE_KEYWORDS = [
    'heart attack', 'myocardial infarction', 'diabetes', 'hypertension',
    'asthma', 'pneumonia', 'tuberculosis', 'malaria', 'dengue',
    'typhoid', 'cholera', 'meningitis', 'epilepsy', 'stroke',
    'anemia', 'sickle cell', 'gout', 'arthritis', 'osteoporosis',
    'glaucoma', 'conjunctivitis', 'otitis media', 'tonsillitis',
    'urinary tract infection', 'kidney stones', 'liver disease',
    'hepatitis', 'cirrhosis', 'peptic ulcer', 'acid reflux',
    'food poisoning', 'scabies', 'impetigo', 'urticaria',
    'depression', 'anxiety', 'bipolar disorder', 'hypothyroidism',
    'hyperthyroidism', 'hypoglycemia', 'anaphylaxis', 'shock',
    'tetanus', 'appendicitis', 'hernia', 'filariasis', 'hookworm',
    'roundworm', 'chickenpox', 'measles', 'mumps', 'pertussis',
    'diphtheria', 'cryptococcal meningitis', 'toxoplasmosis',
    'amoebiasis', 'giardiasis', 'bronchiolitis', 'rickets',
    'protein energy malnutrition', 'neonatal jaundice', 'copd',
    'chronic obstructive pulmonary disease', 'heart failure',
    'congestive cardiac failure', 'goitre', 'sickle cell disease',
    # Added - previously missing, caused fallthrough to weak generic search
    'chikungunya', 'migraine', 'tension headache', 'cluster headache',
    'nephrotic syndrome', 'status epilepticus', 'snake bite',
    'diabetic ketoacidosis', 'dka', 'leptospirosis', 'rabies',
    'organophosphorus poisoning', 'hypocalcemia', 'hypercalcemia',
    'chronic kidney disease', 'acute renal failure', 'vertigo',
    'facial palsy', "parkinson's disease", 'dementia',
    'guillain-barre syndrome', 'febrile seizure', 'pica'
]


class SymptomAgent(BaseAgent):
    """
    User Query -> SymptomAgent -> Retrieval Agent -> Reasoning Agent
    """

    def __init__(self, llm_client: LLMClient = None):
        super().__init__(name="SymptomAgent")
        self.llm_client = llm_client or LLMClient()

    def run(self, user_input: str) -> dict:
        """
        Takes raw user text, returns structured symptoms OR identifies general question.

        Priority order (v2):
        1. Explicit disease name in the query -> use disease name as search term
           (most precise; avoids the LLM inventing generic symptoms for
           "what are the symptoms of X" style questions)
        2. LLM symptom extraction -> use extracted symptoms
        3. General question pattern (what is/how is/etc.) -> use full query
        4. Fallback -> use full query

        Returns dict with:
            - symptoms: extracted symptoms or disease name
            - original_query: the user's full question
            - intent: 'general_knowledge', 'symptom_based', or 'unknown'
        """
        self.log(f"Analyzing input: '{user_input}'")

        # Step 1: Check for an explicit disease name FIRST - most precise signal
        disease = self._extract_disease_from_text(user_input)
        if disease:
            self.log(f"Found disease name in query: {disease}")
            return {
                "symptoms": disease,
                "original_query": user_input,
                "intent": "general_knowledge"
            }

        # Step 2: No disease name found - try LLM symptom extraction
        structured_symptoms = self._extract_symptoms_with_llm(user_input)

        if structured_symptoms and structured_symptoms.upper() != "NO_SYMPTOMS":
            self.log(f"Extracted symptoms: {structured_symptoms}")
            return {
                "symptoms": structured_symptoms,
                "original_query": user_input,
                "intent": "symptom_based"
            }

        # Step 3: Check if it's a "what is", "how is" type question
        self.log("No symptoms explicitly mentioned.")
        if self._is_general_question(user_input):
            self.log("General question detected, using full query.")
            return {
                "symptoms": user_input,
                "original_query": user_input,
                "intent": "general_knowledge"
            }

        # Step 4: Fallback - use the entire query as search term
        self.log("Using entire query as search term.")
        return {
            "symptoms": user_input,
            "original_query": user_input,
            "intent": "unknown"
        }

    def _extract_symptoms_with_llm(self, user_input: str) -> str:
        """Use LLM to extract symptoms from user input."""
        prompt = f"""
You are a medical symptom extraction assistant.

Extract only the key symptoms EXPLICITLY STATED BY THE USER from their message.

Rules:
- Return ONLY comma-separated symptoms.
- Do not explain.
- Do not add extra text.
- Do NOT infer or guess symptoms of a named disease if the user only
  asked about the disease by name (e.g. "what are the symptoms of
  chikungunya" has NO stated symptoms - the user is asking, not
  reporting symptoms they have). In that case return NO_SYMPTOMS.
- If no symptoms are explicitly described by the user, return NO_SYMPTOMS.

User message:
"{user_input}"

Symptoms:
"""
        result = self.llm_client.generate(prompt).strip()
        return result

    def _extract_disease_from_text(self, text: str) -> str:
        """Extract a disease/condition name from text."""
        text_lower = text.lower()
        # Sort by length descending so longer, more specific matches
        # (e.g. "sickle cell disease") are checked before shorter
        # substrings (e.g. "sickle cell") could match prematurely.
        for disease in sorted(DISEASE_KEYWORDS, key=len, reverse=True):
            if disease in text_lower:
                return disease
        return None

    def _is_general_question(self, text: str) -> bool:
        """Check if the query is a general knowledge question."""
        text_lower = text.lower()
        patterns = ['what is', 'what are', 'how is', 'how does',
                   'how to', 'when to', 'why is', 'why does']
        return any(pattern in text_lower for pattern in patterns)


# Testing this file individually
if __name__ == "__main__":
    agent = SymptomAgent()

    test_queries = [
        "What are the warning signs of a heart attack?",
        "I have a really bad headache and I feel hot and tired all the time",
        "What is diabetes?",
        "How is hypertension managed?",
        "What are the symptoms of chikungunya?",
        "What is the recommended treatment for migraine?"
    ]

    for query in test_queries:
        print("-" * 60)
        result = agent.run(query)
        print(f"Query: {query}")
        print(f"Result: {result}")
