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
                "expected_answer": pair["expected_answer"],
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
            "expected_answer": pair["expected_answer"],
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

    save_results_csv(scored_results, "evaluation/results.csv")

    return scored_results, average_score, average_faithfulness


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