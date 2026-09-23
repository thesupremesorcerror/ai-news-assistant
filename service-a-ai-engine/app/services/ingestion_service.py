"""
ingestion_service.py
---------------------
Core RAG ingestion pipeline:

    raw article -> chunk -> embed -> upsert into Qdrant

Kept as plain functions (no framework coupling) so Phase 2's /api/ask
retrieval logic can reuse the chunking/embedding pieces if needed.
"""

import logging
import uuid

from fastapi import HTTPException, status
from qdrant_client.http import models as qmodels

from app.core.config import get_settings
from app.core.embeddings import embed_texts
from app.core.qdrant_client import get_qdrant_client
from app.models.schemas import (
    IngestRequest,
    IngestResponse,
    IngestResultItem,
    NewsArticleIn,
)

logger = logging.getLogger("nemesis_news.ingestion")

settings = get_settings()

# Basic word-based chunking config. Simple on purpose for Phase 1 —
# can be swapped for a smarter recursive/semantic splitter later
# without touching the API contract.
CHUNK_SIZE_WORDS = 150
CHUNK_OVERLAP_WORDS = 30


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE_WORDS, overlap: int = CHUNK_OVERLAP_WORDS) -> list[str]:
    """
    Split article content into overlapping word-count chunks.

    Overlap keeps context from being cut off mid-idea at chunk
    boundaries, which improves retrieval quality for the RAG step
    in Phase 2.
    """
    words = text.split()
    if not words:
        return []

    if len(words) <= chunk_size:
        return [text.strip()]

    chunks = []
    start = 0
    step = max(chunk_size - overlap, 1)  # guard against overlap >= chunk_size
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(words):
            break
        start += step

    return chunks


def _build_points_for_article(article: NewsArticleIn) -> tuple[list[qmodels.PointStruct], int]:
    """
    Chunk one article, embed the chunks, and build Qdrant PointStructs
    carrying the required payload fields (title, content_chunk,
    source_url, published_date).
    """
    chunks = chunk_text(article.content)
    if not chunks:
        return [], 0

    try:
        vectors = embed_texts(chunks)
    except Exception as exc:  # model/runtime failure
        logger.exception("Embedding generation failed for article '%s'", article.title)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to generate embeddings: {exc}",
        ) from exc

    points = [
        qmodels.PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "title": article.title,
                "content_chunk": chunk,
                "source_url": str(article.source_url),
                "published_date": article.published_date.isoformat(),
            },
        )
        for chunk, vector in zip(chunks, vectors)
    ]
    return points, len(chunks)


def ingest_articles(request: IngestRequest) -> IngestResponse:
    """
    Orchestrates the full ingestion pipeline for a batch of articles
    and upserts everything into the `news_embeddings` Qdrant collection.
    """
    client = get_qdrant_client()
    all_points: list[qmodels.PointStruct] = []
    results: list[IngestResultItem] = []

    for article in request.articles:
        points, chunk_count = _build_points_for_article(article)
        if chunk_count == 0:
            logger.warning("Article '%s' produced no chunks (empty content?)", article.title)
            continue

        all_points.extend(points)
        results.append(
            IngestResultItem(
                article_title=article.title,
                chunks_created=chunk_count,
                point_ids=[str(p.id) for p in points],
            )
        )

    if not all_points:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid content found to ingest across the submitted articles.",
        )

    try:
        client.upsert(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            points=all_points,
            wait=True,
        )
    except Exception as exc:
        logger.exception("Qdrant upsert failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to upsert vectors into Qdrant: {exc}",
        ) from exc

    return IngestResponse(
        status="success",
        collection=settings.QDRANT_COLLECTION_NAME,
        total_articles=len(results),
        total_chunks_upserted=len(all_points),
        results=results,
    )
