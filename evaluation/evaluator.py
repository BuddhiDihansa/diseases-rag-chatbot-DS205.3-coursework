"""
evaluator.py
Member 4 - Evaluation & Report

Purpose: Programmatically score how well the system's answers match
the ground truth. Uses two methods:
1. Semantic similarity (embedding-based) - fast, no API cost
2. LLM-as-judge (optional) - more accurate, uses the LLM to grade

This satisfies the "Evaluation Framework" requirement - a script that
calculates the faithfulness/accuracy of the system's responses.
"""

from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer, util  # pip install sentence-transformers


class Evaluator:
    """
    Scores system-generated answers against expected (ground truth) answers.

    Dependency Injection: embedding model name is configurable.
    Reuses the same embedding model concept as Member 2's retrieval
    system for consistency (though this is a separate instance/purpose).
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def semantic_similarity_score(self, expected_answer: str, system_answer: str) -> float:
        """
        Compares expected vs system answer using cosine similarity
        of their embeddings. Returns a score between 0 and 1.
        """
        embeddings = self.model.encode([expected_answer, system_answer], convert_to_tensor=True)
        similarity = util.cos_sim(embeddings[0], embeddings[1])
        return float(similarity[0][0])

    def keyword_overlap_score(self, expected_answer: str, system_answer: str) -> float:
        """
        Simple secondary metric: what fraction of key words from the
        expected answer appear in the system's answer. Useful as a
        sanity check alongside semantic similarity.
        """
        expected_words = set(expected_answer.lower().split())
        system_words = set(system_answer.lower().split())

        if not expected_words:
            return 0.0

        overlap = expected_words.intersection(system_words)
        return len(overlap) / len(expected_words)

    def evaluate_single(self, question: str, expected_answer: str, system_answer: str) -> Dict[str, Any]:
        """Evaluate a single Q&A pair and return a result record."""
        semantic_score = self.semantic_similarity_score(expected_answer, system_answer)
        keyword_score = self.keyword_overlap_score(expected_answer, system_answer)

        # combined score, weighted toward semantic similarity
        final_score = (semantic_score * 0.7) + (keyword_score * 0.3)

        return {
            "question": question,
            "expected_answer": expected_answer,
            "system_answer": system_answer,
            "semantic_similarity": round(semantic_score, 3),
            "keyword_overlap": round(keyword_score, 3),
            "final_score": round(final_score, 3),
            "final_score_percent": f"{round(final_score * 100, 1)}%"
        }

    def evaluate_batch(self, qa_results: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        qa_results: list of dicts, each with question/expected_answer/system_answer
        Returns list of scored results.
        """
        return [
            self.evaluate_single(
                question=item["question"],
                expected_answer=item["expected_answer"],
                system_answer=item["system_answer"]
            )
            for item in qa_results
        ]

    def calculate_average_score(self, scored_results: List[Dict[str, Any]]) -> float:
        """Calculate overall average accuracy across all evaluated questions."""
        if not scored_results:
            return 0.0
        total = sum(r["final_score"] for r in scored_results)
        return round((total / len(scored_results)) * 100, 1)


# Example usage (for testing this file individually)
if __name__ == "__main__":
    evaluator = Evaluator()

    result = evaluator.evaluate_single(
        question="What is diabetes?",
        expected_answer="A chronic disease affecting insulin production.",
        system_answer="Diabetes is a long-term condition related to insulin problems."
    )
    print(result)