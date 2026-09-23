"""
routes/ask.py
--------------
HTTP layer for the RAG query endpoint. Validation + error translation
here; the actual retrieve -> prompt -> generate pipeline lives in
app.services.rag_service.
"""

import logging

from fastapi import APIRouter, HTTPException, status

from app.models.schemas_ask import AskRequest, AskResponse
from app.services.rag_service import answer_query

logger = logging.getLogger("nemesis_news.routes.ask")

router = APIRouter(prefix="/api", tags=["RAG"])


@router.post(
    "/ask",
    response_model=AskResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a question answered via RAG over ingested news articles",
)
def ask(request: AskRequest) -> AskResponse:
    """
    Vectorizes the query, retrieves the top_k most relevant news
    chunks from Qdrant, augments a prompt with that context, and
    returns Gemini's answer along with the source URLs it drew from.
    """
    try:
        return answer_query(request)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error while answering query")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error answering query: {exc}",
        ) from exc
