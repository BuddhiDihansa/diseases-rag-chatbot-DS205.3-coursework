"""
run_evaluation.py
Member 4 - Evaluation & Report
"""

from dotenv import load_dotenv
load_dotenv()

import json
import csv
import time
from evaluation.evaluator import Evaluator
from services.pipeline import MedicalAIPipeline
from utils.exceptions import LLMGenerationError


def load_ground_truth(filepath: str = "evaluation/ground_truth.json") -> list:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["qa_pairs"]


def run_full_evaluation():
    print("Loading ground truth dataset...")
    qa_pairs = load_ground_truth()

    print("Initializing pipeline and evaluator...")
    pipeline = MedicalAIPipeline()
    evaluator = Evaluator()

    qa_results = []

    for pair in qa_pairs:
        print(f"\nRunning question: {pair['question']}")

        try:
            pipeline_output = pipeline.run(pair["question"])
        except LLMGenerationError as e:
            print(f"[ERROR] Skipping this question - LLM call failed: {e}")
            qa_results.append({
                "question": pair["question"],
                "expected_answer": pair["reference_answer"],
                "system_answer": "[ERROR: LLM call failed - rate limited]",
                "faithful": "Error",
                "unsupported_claims": [str(e)],
            })
            print("[INFO] Cooling down for 30s before continuing...")
            time.sleep(30)
            continue

        verification = pipeline_output.get("verification", {})

        qa_results.append({
            "question": pair["question"],
            "expected_answer": pair["reference_answer"],
            "system_answer": pipeline_output["generated_answer"],
            "faithful": verification.get("faithful"),
            "unsupported_claims": verification.get("unsupported_claims", []),
        })

    print("\nScoring all answers...")
    scored_results = evaluator.evaluate_batch(qa_results)

    print("\n" + "=" * 130)
    print(
        f"{'Question':<30} {'Cosine':<8} {'Prec':<8} {'Recall':<8} {'F1':<8} "
        f"{'Score':<8} {'Faithful':<10}"
    )
    print("=" * 130)
    for r in scored_results:
        print(
            f"{r['question'][:28]:<30} "
            f"{r['cosine_similarity']:<8} "
            f"{r['keyword_precision']:<8} "
            f"{r['keyword_recall']:<8} "
            f"{r['keyword_f1']:<8} "
            f"{r['final_score_percent']:<8} "
            f"{str(r['faithful']):<10}"
        )

    average_score = evaluator.calculate_average_score(scored_results)
    average_faithfulness = evaluator.calculate_average_faithfulness(scored_results)
    average_cosine = evaluator.calculate_average_cosine_similarity(scored_results)
    average_precision = evaluator.calculate_average_precision(scored_results)
    average_recall = evaluator.calculate_average_recall(scored_results)
    average_f1 = evaluator.calculate_average_f1(scored_results)

    print("\n" + "=" * 130)
    print(f"OVERALL AVERAGE ACCURACY (blended score): {average_score}%")
    print(f"OVERALL AVERAGE FAITHFULNESS:             {average_faithfulness}%")
    print(f"OVERALL AVERAGE COSINE SIMILARITY:        {average_cosine}%")
    print(f"OVERALL AVERAGE KEYWORD PRECISION:        {average_precision}%")
    print(f"OVERALL AVERAGE KEYWORD RECALL:           {average_recall}%")
    print(f"OVERALL AVERAGE KEYWORD F1:                {average_f1}%")
    print("=" * 130)

    # --- Confusion Matrix (word-level TP/FP/FN/TN) ---
    # See Evaluator.confusion_matrix_counts() docstring for exactly what
    # each cell means. Built from the same expected/system answer pairs
    # already scored above - no extra pipeline runs needed.
    corpus_vocabulary = evaluator.build_corpus_vocabulary(
        [pair["reference_answer"] for pair in qa_pairs]
    )
    per_question_cm = []
    print("\n" + "=" * 90)
    print(f"{'Question':<40} {'TP':<6} {'FP':<6} {'FN':<6} {'TN':<6}")
    print("=" * 90)
    for pair, r in zip(qa_pairs, scored_results):
        counts = evaluator.confusion_matrix_counts(
            r["expected_answer"], r["system_answer"], corpus_vocabulary
        )
        per_question_cm.append(counts)
        print(
            f"{r['question'][:38]:<40} "
            f"{counts['TP']:<6} {counts['FP']:<6} {counts['FN']:<6} {counts['TN']:<6}"
        )

    cm_summary = evaluator.summarize_confusion_matrix(per_question_cm)
    print("=" * 90)
    print(f"{'TOTAL':<40} "
          f"{cm_summary['TP']:<6} {cm_summary['FP']:<6} {cm_summary['FN']:<6} {cm_summary['TN']:<6}")
    print("=" * 90)
    print(f"Precision: {cm_summary['precision']}   Recall: {cm_summary['recall']}   "
          f"F1: {cm_summary['f1']}   Accuracy: {cm_summary['accuracy']}")
    print("=" * 90)

    save_confusion_matrix_csv(qa_pairs, per_question_cm, cm_summary, "evaluation/confusion_matrix.csv")

    save_results_csv(scored_results, "evaluation/results.csv")

    return scored_results, average_score, average_faithfulness


def save_confusion_matrix_csv(qa_pairs: list, per_question_cm: list, cm_summary: dict, output_path: str):
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["question", "TP", "FP", "FN", "TN"])
        writer.writeheader()
        for pair, counts in zip(qa_pairs, per_question_cm):
            writer.writerow({"question": pair["question"], **counts})
        writer.writerow({
            "question": "TOTAL",
            "TP": cm_summary["TP"], "FP": cm_summary["FP"],
            "FN": cm_summary["FN"], "TN": cm_summary["TN"],
        })
        writer.writerow({
            "question": f"precision={cm_summary['precision']} recall={cm_summary['recall']} "
                        f"f1={cm_summary['f1']} accuracy={cm_summary['accuracy']}",
            "TP": "", "FP": "", "FN": "", "TN": "",
        })

    print(f"Confusion matrix saved to {output_path}")


def save_results_csv(scored_results: list, output_path: str):
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "question", "expected_answer", "system_answer",
            "cosine_similarity", "keyword_precision", "keyword_recall", "keyword_f1",
            "faithful", "faithfulness_score", "unsupported_claims",
            "final_score_percent",
        ])
        writer.writeheader()
        for row in scored_results:
            writer.writerow({k: row[k] for k in writer.fieldnames})

    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    run_full_evaluation()