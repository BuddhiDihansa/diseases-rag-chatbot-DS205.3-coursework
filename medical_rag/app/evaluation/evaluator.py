"""
Empirical evaluation framework.
Runs ground-truth Q&A pairs through the RAG system and scores responses.
Usage: python -m app.evaluation.evaluator
"""
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.ingestion.pdf_loader import PDFIngester
from app.vectorstore.chroma_store import ChromaVectorStore
from app.retrieval.retriever import MedicalRetriever
from app.generation.llm_generator import GroqGenerator
from groq import Groq


EVAL_SYSTEM_PROMPT = """You are an evaluation judge for a medical RAG system.
Compare the GENERATED ANSWER against the GROUND TRUTH ANSWER.

Score the faithfulness from 0 to 10:
- 10: Completely accurate, matches ground truth perfectly.
- 7-9: Mostly correct, minor omissions.
- 4-6: Partially correct, some key facts missing.
- 1-3: Mostly wrong or hallucinated.
- 0: Completely wrong or harmful.

Respond ONLY with JSON: {"score": <int>, "reason": "<brief explanation>"}"""


class RAGEvaluator:
    """
    Runs a ground-truth dataset through the full RAG pipeline
    and produces an accuracy report.
    """

    def __init__(
        self,
        retriever: MedicalRetriever,
        generator: GroqGenerator,
        ground_truth_path: str = "data/ground_truth.json",
    ):
        self.retriever = retriever
        self.generator = generator
        self.ground_truth_path = ground_truth_path
        self.judge_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def load_ground_truth(self):
        with open(self.ground_truth_path, "r") as f:
            return json.load(f)

    def judge_answer(self, question: str, ground_truth: str, generated: str) -> dict:
        """Use LLM-as-judge to score the generated answer."""
        prompt = f"""QUESTION: {question}
GROUND TRUTH: {ground_truth}
GENERATED ANSWER: {generated}"""

        response = self.judge_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": EVAL_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=200,
        )
        raw = response.choices[0].message.content.strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"score": 0, "reason": "Judge failed to parse."}

    def run(self) -> None:
        """Run full evaluation and print results table."""
        dataset = self.load_ground_truth()
        results = []
        total_score = 0

        print("\n" + "=" * 80)
        print("MEDICAL RAG SYSTEM — EMPIRICAL EVALUATION")
        print("=" * 80)

        for i, item in enumerate(dataset, 1):
            question = item["question"]
            ground_truth = item["answer"]

            # Retrieve + Generate (the full agentic loop)
            chunks = self.retriever.retrieve(question)
            context = self.retriever.format_context(chunks)
            generated = self.generator.generate(question, context)

            # Judge
            judgment = self.judge_answer(question, ground_truth, generated)
            score = judgment.get("score", 0)
            total_score += score

            results.append({
                "id": i,
                "question": question,
                "ground_truth": ground_truth,
                "generated": generated,
                "score": score,
                "reason": judgment.get("reason", ""),
            })

            print(f"\n[Q{i}] {question}")
            print(f"  Ground Truth : {ground_truth[:120]}...")
            print(f"  Generated    : {generated[:120]}...")
            print(f"  Score        : {score}/10 — {judgment.get('reason', '')}")

        avg_score = total_score / len(dataset) if dataset else 0
        print("\n" + "=" * 80)
        print(f"AVERAGE FAITHFULNESS SCORE: {avg_score:.1f} / 10")
        print(f"TOTAL QUESTIONS EVALUATED: {len(dataset)}")
        print("=" * 80)

        # Save results to JSON
        output_path = "data/eval_results.json"
        with open(output_path, "w") as f:
            json.dump({"average_score": avg_score, "results": results}, f, indent=2)
        print(f"\nDetailed results saved to {output_path}")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    persist_dir = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    collection = os.getenv("COLLECTION_NAME", "medical_docs")
    embed_model = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")

    store = ChromaVectorStore(persist_dir, collection, embed_model)
    retriever = MedicalRetriever(store)
    generator = GroqGenerator()

    evaluator = RAGEvaluator(retriever, generator)
    evaluator.run()
