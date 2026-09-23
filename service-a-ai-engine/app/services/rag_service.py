"""
rag_service.py
---------------
Orchestrates the full RAG answer pipeline for POST /api/ask:

    query -> retrieve top_k chunks (Qdrant)
          -> build augmented prompt
          -> call Gemini
          -> return answer + deduped source URLs
"""

import logging

from app.models.schemas_ask import AskRequest, AskResponse
from app.services.gemini_service import build_augmented_prompt, generate_answer
from app.services.retrieval_service import retrieve_relevant_chunks

logger = logging.getLogger("nemesis_news.rag")


def answer_query(request: AskRequest) -> AskResponse:
    chunks = retrieve_relevant_chunks(request.query, top_k=request.top_k)

    prompt = build_augmented_prompt(request.query, chunks)
    answer = generate_answer(prompt)

    # De-dupe source URLs while preserving retrieval order (relevance order).
    seen = set()
    sources: list[str] = []
    for chunk in chunks:
        if chunk.source_url and chunk.source_url not in seen:
            seen.add(chunk.source_url)
            sources.append(chunk.source_url)

    return AskResponse(
        query=request.query,
        answer=answer,
        sources=sources,
        retrieved_chunks=chunks,
    )
