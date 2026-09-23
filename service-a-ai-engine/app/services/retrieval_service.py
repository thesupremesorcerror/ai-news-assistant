"""
retrieval_service.py
---------------------
Vector-search half of the RAG pipeline: takes a raw user query,
embeds it with the same model used at ingestion time, and searches
the `news_embeddings` Qdrant collection for the top_k most similar
chunks.
"""

import logging

from fastapi import HTTPException, status

from app.core.config import get_settings
from app.core.embeddings import embed_texts
from app.core.qdrant_client import get_qdrant_client
from app.models.schemas_ask import RetrievedChunk

logger = logging.getLogger("nemesis_news.retrieval")

settings = get_settings()


def retrieve_relevant_chunks(query: str, top_k: int = 3) -> list[RetrievedChunk]:
    """
    Embed the query and run a similarity search against Qdrant.
    Returns an empty list (not an error) if nothing is found —
    the caller decides how to handle "no context" in the prompt.
    """
    try:
        query_vector = embed_texts([query])[0]
    except Exception as exc:
        logger.exception("Failed to embed query for retrieval")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to generate query embedding: {exc}",
        ) from exc

    client = get_qdrant_client()

    try:
        search_result = client.search(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query_vector=query_vector,
            limit=top_k,
            with_payload=True,
        )
    except Exception as exc:
        logger.exception("Qdrant search failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Vector search failed: {exc}",
        ) from exc

    chunks: list[RetrievedChunk] = []
    for point in search_result:
        payload = point.payload or {}
        chunks.append(
            RetrievedChunk(
                title=payload.get("title", "Unknown"),
                content_chunk=payload.get("content_chunk", ""),
                source_url=payload.get("source_url", ""),
                published_date=payload.get("published_date", ""),
                score=point.score,
            )
        )

    return chunks
