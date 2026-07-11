"""
run_evaluation.py
Member 4 - Evaluation & Report

Purpose: Main script to run - loads ground truth questions, runs them
through the full pipeline (Members 2 & 3's work), scores the answers,
and outputs a results table. This is exactly what the report's
"Empirical Evaluation" section (IV) needs, and what gets shown
running in the demo video.
"""

import json
import csv
from evaluation.evaluator import Evaluator
from services.pipeline import MedicalAIPipeline


def load_ground_truth(filepath: str = "evaluation/ground_truth.json") -> list:
    """Load the ground truth Q&A pairs from JSON."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["qa_pairs"]


def run_full_evaluation():
    """
    Runs every ground truth question through the pipeline,
    scores each answer, and prints/saves a results table.
    """
    print("Loading ground truth dataset...")
    qa_pairs = load_ground_truth()

    print("Initializing pipeline and evaluator...")
    pipeline = MedicalAIPipeline()
    evaluator = Evaluator()

    qa_results = []

    import time

    for pair in qa_pairs:
        print(f"\nRunning question: {pair['question']}")
        pipeline_output = pipeline.run(pair["question"])
        time.sleep(3)

        qa_results.append({
            "question": pair["question"],
            "expected_answer": pair["expected_answer"],
            "system_answer": pipeline_output["generated_answer"]
        })

    print("\nScoring all answers...")
    scored_results = evaluator.evaluate_batch(qa_results)

    # print results table to console
    print("\n" + "=" * 100)
    print(f"{'Question':<40} {'Expected':<20} {'Score':<10}")
    print("=" * 100)
    for r in scored_results:
        print(f"{r['question'][:38]:<40} {r['expected_answer'][:18]:<20} {r['final_score_percent']:<10}")

    average_score = evaluator.calculate_average_score(scored_results)
    print("\n" + "=" * 100)
    print(f"OVERALL AVERAGE ACCURACY: {average_score}%")
    print("=" * 100)

    # save to CSV for the report (Table format required in section IV)
    save_results_csv(scored_results, "evaluation/results.csv")

    return scored_results, average_score


def save_results_csv(scored_results: list, output_path: str):
    """Save results to CSV so they can be pasted into the report table."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "question", "expected_answer", "system_answer",
            "semantic_similarity", "keyword_overlap", "final_score_percent"
        ])
        writer.writeheader()
        for row in scored_results:
            writer.writerow({k: row[k] for k in writer.fieldnames})

    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    run_full_evaluation()