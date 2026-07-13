"""
evaluator.py
Member 4 - Evaluation & Report

Purpose: Programmatically score how well the system's answers match
the ground truth, AND how faithful the answer is to the retrieved
context.
"""

import re
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer, util  # pip install sentence-transformers
from nltk.stem import PorterStemmer  # pip install nltk (no extra data download needed)


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
        self.stemmer = PorterStemmer()

    def semantic_similarity_score(self, expected_answer: str, system_answer: str) -> float:
        """
        Cosine similarity between the sentence-transformer embeddings
        of the expected vs system answer.
        """
        embeddings = self.model.encode([expected_answer, system_answer], convert_to_tensor=True)
        similarity = util.cos_sim(embeddings[0], embeddings[1])
        return float(similarity[0][0])

    def _tokenize(self, text: str) -> set:
        """
        Lowercase word tokens, punctuation stripped, then stemmed with
        the Porter algorithm so word-form variants count as the same
        token - "symptoms"/"symptom", "managed"/"manage",
        "bleeding"/"bleed" all reduce to one shared stem. Without this,
        two answers that are correct and mean exactly the same thing
        can score zero overlap purely because one used the plural and
        the other the singular, which has nothing to do with whether
        the system's answer is actually right.
        """
        words = re.findall(r"[a-z0-9']+", text.lower())
        return set(self.stemmer.stem(w) for w in words)

    def keyword_recall_score(self, expected_answer: str, system_answer: str) -> float:
        """
        Of the words in the expected (ground-truth) answer, what
        fraction also appear in the system's answer.
        """
        expected_words = self._tokenize(expected_answer)
        system_words = self._tokenize(system_answer)
        if not expected_words:
            return 0.0
        overlap = expected_words.intersection(system_words)
        return len(overlap) / len(expected_words)

    def keyword_precision_score(self, expected_answer: str, system_answer: str) -> float:
        """
        Of the words in the SYSTEM's answer, what fraction also appear
        in the expected answer.
        """
        expected_words = self._tokenize(expected_answer)
        system_words = self._tokenize(system_answer)
        if not system_words:
            return 0.0
        overlap = expected_words.intersection(system_words)
        return len(overlap) / len(system_words)

    def keyword_f1_score(self, precision: float, recall: float) -> float:
        """Harmonic mean of precision and recall. 0 if both are 0."""
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)

    def keyword_overlap_score(self, expected_answer: str, system_answer: str) -> float:
        return self.keyword_recall_score(expected_answer, system_answer)

    def confusion_matrix_counts(
        self, expected_answer: str, system_answer: str, corpus_vocabulary: set
    ) -> Dict[str, int]:
        """
        Word-level confusion matrix for a single question, treating
        "is this word part of the correct answer" as the binary label:

        - TP: word IS in the expected answer AND the system DID say it
              (a correct fact the system got right)
        - FN: word IS in the expected answer but the system did NOT say it
              (a correct fact the system missed)
        - FP: word is NOT in the expected answer but the system said it
              anyway (extra content beyond the reference answer)
        - TN: word is NOT in the expected answer for THIS question, AND
              the system correctly did not say it either. Since "not in
              the expected answer" is trivially true for almost any
              random word, TN is computed against corpus_vocabulary -
              the set of all meaningful words that appear anywhere across
              the whole ground-truth dataset (i.e. words that matter to
              THIS evaluation, not the entire English language). This
              keeps TN meaningful: it counts terms that are relevant to
              OTHER questions in the test set but were correctly left out
              of this answer, rather than crediting the system for every
              word in the dictionary it didn't happen to use.

        corpus_vocabulary: pass the union of tokenized words from every
        reference_answer in the ground truth set (build this once per
        evaluation run - see build_corpus_vocabulary()).
        """
        expected_words = self._tokenize(expected_answer)
        system_words = self._tokenize(system_answer)

        tp = len(expected_words & system_words)
        fn = len(expected_words - system_words)
        fp = len(system_words - expected_words)
        tn = len((corpus_vocabulary - expected_words) - system_words)

        return {"TP": tp, "FP": fp, "FN": fn, "TN": tn}

    def build_corpus_vocabulary(self, all_reference_answers: List[str]) -> set:
        """
        Union of tokenized words across every reference_answer in the
        ground truth set. Used as the shared vocabulary for the TN count
        in confusion_matrix_counts() - see that method's docstring.
        """
        vocab = set()
        for answer in all_reference_answers:
            vocab |= self._tokenize(answer)
        return vocab

    def summarize_confusion_matrix(
        self, per_question_counts: List[Dict[str, int]]
    ) -> Dict[str, Any]:
        """
        Aggregates per-question TP/FP/FN/TN into dataset-wide totals and
        the standard derived metrics (precision, recall, F1, accuracy).
        """
        total_tp = sum(c["TP"] for c in per_question_counts)
        total_fp = sum(c["FP"] for c in per_question_counts)
        total_fn = sum(c["FN"] for c in per_question_counts)
        total_tn = sum(c["TN"] for c in per_question_counts)

        precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) else 0.0
        recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
        denom = total_tp + total_tn + total_fp + total_fn
        accuracy = (total_tp + total_tn) / denom if denom else 0.0

        return {
            "TP": total_tp, "FP": total_fp, "FN": total_fn, "TN": total_tn,
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1": round(f1, 3),
            "accuracy": round(accuracy, 3),
        }

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
        keyword_recall = self.keyword_recall_score(expected_answer, system_answer)
        keyword_precision = self.keyword_precision_score(expected_answer, system_answer)
        keyword_f1 = self.keyword_f1_score(keyword_precision, keyword_recall)
        faith_score = self.faithfulness_score(faithful_verdict) if faithful_verdict else None

        correctness_score = (semantic_score * 0.7) + (keyword_recall * 0.3)

        if faith_score is not None:
            final_score = (correctness_score * 0.6) + (faith_score * 0.4)
        else:
            final_score = correctness_score

        return {
            "question": question,
            "expected_answer": expected_answer,
            "system_answer": system_answer,
            "cosine_similarity": round(semantic_score, 3),
            "keyword_precision": round(keyword_precision, 3),
            "keyword_recall": round(keyword_recall, 3),
            "keyword_f1": round(keyword_f1, 3),
            "semantic_similarity": round(semantic_score, 3),
            "keyword_overlap": round(keyword_recall, 3),
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

    def _average_metric(self, scored_results: List[Dict[str, Any]], key: str) -> float:
        if not scored_results:
            return 0.0
        return round((sum(r[key] for r in scored_results) / len(scored_results)) * 100, 1)

    def calculate_average_cosine_similarity(self, scored_results: List[Dict[str, Any]]) -> float:
        return self._average_metric(scored_results, "cosine_similarity")

    def calculate_average_precision(self, scored_results: List[Dict[str, Any]]) -> float:
        return self._average_metric(scored_results, "keyword_precision")

    def calculate_average_recall(self, scored_results: List[Dict[str, Any]]) -> float:
        return self._average_metric(scored_results, "keyword_recall")

    def calculate_average_f1(self, scored_results: List[Dict[str, Any]]) -> float:
        return self._average_metric(scored_results, "keyword_f1")


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