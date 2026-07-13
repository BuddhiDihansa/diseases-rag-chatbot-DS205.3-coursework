"""
query_expander.py
Member 2 - Retrieval & Vector Database

Purpose: Generate alternate phrasings of a user's query so retrieval
isn't limited to matching the exact words the user typed.

Why this matters: clinical guideline PDFs use formal/technical
vocabulary ("contraindicated", "NSAID") that a layperson's question
("what should someone with dengue avoid?") won't lexically match, even
though it's asking about exactly that fact. This is "vocabulary
mismatch" - a well-documented limitation of BM25 (exact keyword
matching) and, to a lesser degree, of vector search too (the query and
the answer sentence can be semantically related but phrased so
differently that their embeddings end up further apart than expected).

Multi-query retrieval addresses this directly: instead of one search,
we run the hybrid search (BM25 + vector + reranker) once per query
variant and merge the results, so a chunk only needs to match ONE
phrasing of the question to be found - not necessarily the user's
original wording.
"""

from typing import List
from services.llm_client import LLMClient


class QueryExpander:
    """
    Wraps an LLMClient to turn one user query into several alternate
    phrasings ("expansions"), used by RetrieverAgent for multi-query
    retrieval. See module docstring above for the motivation.
    """

    def __init__(self, llm_client: LLMClient = None, num_variants: int = 1):
        self.llm_client = llm_client or LLMClient()
        self.num_variants = num_variants

    def expand(self, query: str) -> List[str]:
        """
        Returns a list starting with the original query, followed by
        up to num_variants alternate phrasings:
            [original_query, variant_1, variant_2, ...]

        Query expansion is a retrieval quality *enhancement*, not a
        hard dependency - if the LLM call fails for any reason
        (rate limit, network error, malformed output), this falls back
        to just [original_query] rather than raising, so a transient
        failure here never breaks retrieval entirely.
        """
        prompt = f"""You are a medical search query rewriting assistant.

Given a user's medical question, generate ONLY ONE alternative
clinical search query using medical terminology. that a formal clinical guideline document would more
likely use similar vocabulary to. Prefer clinical/technical terms over
layperson terms where a natural equivalent exists - for example:
- "avoid" -> "contraindicated", "should not take"
- "medicines to avoid" -> "drug interactions", "NSAID", "aspirin"
- "warning signs" -> "clinical presentation", "case definition"

Return ONLY the {self.num_variants} rewritten queries, one per line, in
plain text - no numbering, no bullet points, no explanation, nothing
else.

Original question: "{query}"

Rewritten queries:"""

        try:
            raw_output = self.llm_client.generate(prompt, max_tokens=60)
            variants = [
                line.strip("-•*0123456789. \t")
                for line in raw_output.strip().split("\n")
                if line.strip()
            ]
            # Guard against the LLM echoing the original query back as
            # one of the "variants" - that would just waste a search.
            variants = [
                v for v in variants
                if v and v.lower() != query.strip().lower()
            ][: self.num_variants]
        except Exception as e:
            print(f"[QueryExpander] WARNING: query expansion failed "
                  f"({e}). Falling back to the original query only.")
            variants = []

        return [query] + variants


# Example usage (for testing this file individually)
if __name__ == "__main__":
    expander = QueryExpander()
    variants = expander.expand("What should someone with dengue avoid?")
    print("Query variants:")
    for v in variants:
        print(f"  - {v}")