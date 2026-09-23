"""
routes/ingest.py
-----------------
HTTP layer for ingestion. Keeps request validation + error translation
here, delegates actual chunk/embed/upsert work to the service layer.
"""

import logging

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import IngestRequest, IngestResponse
from app.services.ingestion_service import ingest_articles

logger = logging.getLogger("nemesis_news.routes.ingest")

router = APIRouter(prefix="/api", tags=["Ingestion"])


@router.post(
    "/ingest",
    response_model=IngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest a batch of news articles into the vector store",
)
def ingest(request: IngestRequest) -> IngestResponse:
    """
    Accepts a list of news articles, chunks + embeds their content,
    and upserts the resulting vectors into the `news_embeddings`
    Qdrant collection so they can later be retrieved by /api/ask
    (Phase 2).
    """
    try:
        return ingest_articles(request)
    except HTTPException:
        # Already a well-formed HTTP error from the service layer — re-raise as-is.
        raise
    except Exception as exc:  # last-resort safety net
        logger.exception("Unexpected error during ingestion")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected ingestion error: {exc}",
        ) from exc
