"""
test_evaluation.py
Tests for Member 4's evaluation module (evaluator, ground truth loading)

Run with: pytest tests/test_evaluation.py -v
"""

import pytest
import json
import os
from evaluation.evaluator import Evaluator


class TestEvaluator:

    def setup_method(self):
        self.evaluator = Evaluator()

    def test_identical_answers_score_high(self):
        score = self.evaluator.semantic_similarity_score(
            expected_answer="Diabetes causes high blood sugar.",
            system_answer="Diabetes causes high blood sugar."
        )
        assert score > 0.95  # near-identical text should score very high

    def test_unrelated_answers_score_low(self):
        score = self.evaluator.semantic_similarity_score(
            expected_answer="Diabetes causes high blood sugar.",
            system_answer="The weather is sunny today."
        )
        assert score < 0.5

    def test_similar_meaning_different_words_scores_reasonably(self):
        score = self.evaluator.semantic_similarity_score(
            expected_answer="Diabetes is a chronic disease affecting insulin.",
            system_answer="Diabetes is a long-term condition related to insulin problems."
        )
        assert score > 0.6  # different words, same meaning - should still score well

    def test_evaluate_single_returns_all_fields(self):
        result = self.evaluator.evaluate_single(
            question="What is diabetes?",
            expected_answer="A chronic disease affecting insulin.",
            system_answer="Diabetes is a chronic insulin-related disease."
        )
        assert "final_score" in result
        assert "semantic_similarity" in result
        assert "keyword_overlap" in result
        assert 0 <= result["final_score"] <= 1

    def test_average_score_calculation(self):
        fake_results = [
            {"final_score": 0.9},
            {"final_score": 0.7},
            {"final_score": 0.5}
        ]
        average = self.evaluator.calculate_average_score(fake_results)
        assert average == 70.0  # (0.9+0.7+0.5)/3 * 100 = 70.0


class TestGroundTruthFile:

    def test_ground_truth_file_exists(self):
        assert os.path.exists("evaluation/ground_truth.json")

    def test_ground_truth_has_at_least_10_questions(self):
        with open("evaluation/ground_truth.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["qa_pairs"]) >= 10  # assignment requirement

    def test_each_qa_pair_has_required_fields(self):
        with open("evaluation/ground_truth.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        for pair in data["qa_pairs"]:
            assert "question" in pair
            assert "reference_answer" in pair


if __name__ == "__main__":
    pytest.main([__file__, "-v"])