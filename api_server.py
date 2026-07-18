"""
api_server.py
HTTP API layer for the Next.js frontend (mediguide-web).

Purpose: Wraps the existing MedicalAIPipeline (services/pipeline.py) -
built for Member 2/3's CLI (main.py) - behind a small FastAPI app so a
separate Next.js frontend can call it over HTTP instead of running the
Python pipeline directly.

Nothing in the existing pipeline/agents/retrieval code is changed here;
this is purely an adapter layer. Run with:

    uvicorn api_server:app --reload --port 8000

Endpoints:
    GET  /api/health   -> quick check that the server + pipeline are up
    POST /api/chat      -> run one query through the full agent pipeline
"""

import os

# Must run before any `transformers`/`sentence_transformers` import
# (pulled in indirectly via services.pipeline below). Some environments
# have a `tensorflow` package installed alongside `transformers`, which
# makes transformers try to load its TensorFlow/Keras integration on
# startup - and crash if the installed Keras is Keras 3 (transformers
# only supports the legacy tf-keras). sentence-transformers only ever
# uses the PyTorch backend here, so TensorFlow isn't needed at all -
# this just stops transformers from probing for it.
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")

import re
import time
from typing import List, Optional

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.pipeline import MedicalAIPipeline
from utils.exceptions import LLMGenerationError, ConfigurationError
from utils.logger import get_logger

logger = get_logger("APIServer")

app = FastAPI(title="MediGuide LK API", version="1.0.0")

# Comma-separated list of allowed frontend origins, e.g.
# "http://localhost:3000,https://mediguide-lk.vercel.app"
_allowed_origins = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _allowed_origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# The pipeline (and every agent/model it loads) is expensive to build,
# so it's created once at startup and reused across requests - NOT
# once per request.
_pipeline: Optional[MedicalAIPipeline] = None


@app.on_event("startup")
def load_pipeline():
    global _pipeline
    logger.info("Loading MedicalAIPipeline (this loads the embedding + "
                "reranker models, can take a moment)...")
    try:
        _pipeline = MedicalAIPipeline()
        logger.info("Pipeline ready.")
    except ConfigurationError as e:
        # Don't crash the whole server over a missing API key - surface
        # a clear error on every request instead, so the frontend can
        # show something actionable rather than a connection failure.
        logger.error(f"Pipeline failed to initialize: {e}")
        _pipeline = None


class ChatRequest(BaseModel):
    message: str


class Citation(BaseModel):
    source: str
    snippet: str


class ChatResponse(BaseModel):
    user_query: str
    structured_symptoms: str
    is_informational: bool
    answer: str
    citations: List[Citation]
    faithful: str
    unsupported_claims: List[str]
    needs_review: bool
    response_time_seconds: float


# Matches the "[Source: file.pdf, page 3]" tags that
# RetrieverAgent.get_context_text() prefixes onto every retrieved chunk
# (see retrieval/retriever_agent.py) - used here to split the combined
# context string back into individual citation cards for the UI,
# without changing anything in the retrieval module itself.
_SOURCE_TAG = re.compile(r"\[Source:\s*(.*?)\]\s*\n?", re.DOTALL)


def _extract_citations(retrieved_context: str) -> List[Citation]:
    if not retrieved_context or not retrieved_context.strip():
        return []

    parts = _SOURCE_TAG.split(retrieved_context)
    # re.split with a capturing group returns:
    # [text_before_first_match, group1, text_after, group2, text_after, ...]
    citations = []
    for i in range(1, len(parts), 2):
        source = parts[i].strip()
        snippet = parts[i + 1].strip() if i + 1 < len(parts) else ""
        # keep snippets short for the UI - full text is still grounding
        # the answer, this is just a preview card
        if len(snippet) > 280:
            snippet = snippet[:280].rsplit(" ", 1)[0] + "…"
        citations.append(Citation(source=source, snippet=snippet))
    return citations


@app.get("/api/health")
def health():
    return {
        "status": "ok" if _pipeline is not None else "pipeline_unavailable",
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if _pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Pipeline is not available - check the server's "
                   "LLM_API_KEY configuration.",
        )

    message = req.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="message cannot be empty.")

    start = time.time()
    try:
        result = _pipeline.run(message)
    except LLMGenerationError as e:
        logger.error(f"LLM generation failed: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"The language model API failed after retries: {e}",
        )

    elapsed = round(time.time() - start, 2)

    return ChatResponse(
        user_query=result["user_query"],
        structured_symptoms=result["structured_symptoms"],
        is_informational=result["structured_symptoms"] == message,
        answer=result["generated_answer"],
        citations=_extract_citations(result["retrieved_context"]),
        faithful=result["verification"]["faithful"],
        unsupported_claims=result["verification"]["unsupported_claims"],
        needs_review=result["needs_review"],
        response_time_seconds=elapsed,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)