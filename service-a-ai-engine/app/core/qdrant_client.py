"""
qdrant_client.py
----------------
Owns the single QdrantClient instance for the app and makes sure the
`news_embeddings` collection exists with the right vector size before
any ingestion/search happens.
"""

import logging

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from qdrant_client.http.exceptions import UnexpectedResponse

from app.core.config import get_settings

logger = logging.getLogger("nemesis_news.qdrant")

settings = get_settings()

# A single shared client for the process. QdrantClient is thread-safe
# for the HTTP transport used here, so a module-level singleton is fine.
_client: QdrantClient | None = None


def get_qdrant_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )
    return _client


def ensure_collection_exists() -> None:
    """
    Idempotently create the news_embeddings collection if it doesn't
    already exist. Called once on app startup (see main.py lifespan).
    """
    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION_NAME

    try:
        client.get_collection(collection_name)
        logger.info("Qdrant collection '%s' already exists.", collection_name)
    except (UnexpectedResponse, ValueError):
        logger.info("Creating Qdrant collection '%s'...", collection_name)
        client.create_collection(
            collection_name=collection_name,
            vectors_config=qmodels.VectorParams(
                size=settings.EMBEDDING_DIMENSION,
                distance=qmodels.Distance.COSINE,
            ),
        )
        logger.info("Qdrant collection '%s' created.", collection_name)
