"""
evaluator.py
Member 4 - Evaluation & Report

Purpose: Programmatically score how well the system's answers match
the ground truth, AND how faithful the answer is to the retrieved
context.
"""

from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer, util  # pip install sentence-transformers


class Evaluator:
    """
    Scores system-generated answers against expected (ground truth) answers,
    and against the retrieved context (faithfulness).
    """

    FAITHFUL_SCORE_MAP = {
        "Yes": 1.0,
        "Partially": 0.5,
        "No": 0.0,
    }

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def semantic_similarity_score(self, expected_answer: str, system_answer: str) -> float:
        embeddings = self.model.encode([expected_answer, system_answer], convert_to_tensor=True)
        similarity = util.cos_sim(embeddings[0], embeddings[1])
        return float(similarity[0][0])

    def keyword_overlap_score(self, expected_answer: str, system_answer: str) -> float:
        expected_words = set(expected_answer.lower().split())
        system_words = set(system_answer.lower().split())
        if not expected_words:
            return 0.0
        overlap = expected_words.intersection(system_words)
        return len(overlap) / len(expected_words)

    def faithfulness_score(self, faithful_verdict: str) -> float:
        return self.FAITHFUL_SCORE_MAP.get(faithful_verdict, 0.5)

    def evaluate_single(
        self,
        question: str,
        expected_answer: str,
        system_answer: str,
        faithful_verdict: str = None,
        unsupported_claims: list = None,
    ) -> Dict[str, Any]:
        semantic_score = self.semantic_similarity_score(expected_answer, system_answer)
        keyword_score = self.keyword_overlap_score(expected_answer, system_answer)
        faith_score = self.faithfulness_score(faithful_verdict) if faithful_verdict else None

        correctness_score = (semantic_score * 0.7) + (keyword_score * 0.3)

        if faith_score is not None:
            final_score = (correctness_score * 0.6) + (faith_score * 0.4)
        else:
            final_score = correctness_score

        return {
            "question": question,
            "expected_answer": expected_answer,
            "system_answer": system_answer,
            "semantic_similarity": round(semantic_score, 3),
            "keyword_overlap": round(keyword_score, 3),
            "faithful": faithful_verdict if faithful_verdict else "N/A",
            "faithfulness_score": round(faith_score, 3) if faith_score is not None else "N/A",
            "unsupported_claims": "; ".join(unsupported_claims) if unsupported_claims else "",
            "final_score": round(final_score, 3),
            "final_score_percent": f"{round(final_score * 100, 1)}%",
        }

    def evaluate_batch(self, qa_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            self.evaluate_single(
                question=item["question"],
                expected_answer=item["expected_answer"],
                system_answer=item["system_answer"],
                faithful_verdict=item.get("faithful"),
                unsupported_claims=item.get("unsupported_claims"),
            )
            for item in qa_results
        ]

    def calculate_average_score(self, scored_results: List[Dict[str, Any]]) -> float:
        if not scored_results:
            return 0.0
        total = sum(r["final_score"] for r in scored_results)
        return round((total / len(scored_results)) * 100, 1)

    def calculate_average_faithfulness(self, scored_results: List[Dict[str, Any]]) -> float:
        scores = [r["faithfulness_score"] for r in scored_results if r["faithfulness_score"] != "N/A"]
        if not scores:
            return 0.0
        return round((sum(scores) / len(scores)) * 100, 1)


if __name__ == "__main__":
    evaluator = Evaluator()
    result = evaluator.evaluate_single(
        question="What is diabetes?",
        expected_answer="A chronic disease affecting insulin production.",
        system_answer="Diabetes is a long-term condition related to insulin problems.",
        faithful_verdict="Yes",
        unsupported_claims=[],
    )
    print(result)