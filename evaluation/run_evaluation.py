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

    print("\n" + "=" * 115)
    print(f"{'Question':<35} {'Expected':<18} {'Score':<10} {'Faithful':<10} {'FaithScore':<10}")
    print("=" * 115)
    for r in scored_results:
        print(
            f"{r['question'][:33]:<35} "
            f"{r['expected_answer'][:16]:<18} "
            f"{r['final_score_percent']:<10} "
            f"{str(r['faithful']):<10} "
            f"{str(r['faithfulness_score']):<10}"
        )

    average_score = evaluator.calculate_average_score(scored_results)
    average_faithfulness = evaluator.calculate_average_faithfulness(scored_results)

    print("\n" + "=" * 115)
    print(f"OVERALL AVERAGE ACCURACY:     {average_score}%")
    print(f"OVERALL AVERAGE FAITHFULNESS: {average_faithfulness}%")
    print("=" * 115)

    save_results_csv(scored_results, "evaluation/results.csv")

    return scored_results, average_score, average_faithfulness


def save_results_csv(scored_results: list, output_path: str):
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "question", "expected_answer", "system_answer",
            "semantic_similarity", "keyword_overlap",
            "faithful", "faithfulness_score", "unsupported_claims",
            "final_score_percent",
        ])
        writer.writeheader()
        for row in scored_results:
            writer.writerow({k: row[k] for k in writer.fieldnames})

    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    run_full_evaluation()