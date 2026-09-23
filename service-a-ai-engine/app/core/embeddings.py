"""
embeddings.py
-------------
Loads the sentence-transformers model once (it's expensive to load)
and exposes a simple encode() helper used by the ingestion and
(in Phase 2) query pipelines.
"""

import logging
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import get_settings

logger = logging.getLogger("nemesis_news.embeddings")


@lru_cache
def get_embedding_model() -> SentenceTransformer:
    settings = get_settings()
    logger.info("Loading embedding model '%s'...", settings.EMBEDDING_MODEL_NAME)
    model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    logger.info("Embedding model loaded.")
    return model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Encode a batch of text chunks into dense vectors."""
    model = get_embedding_model()
    vectors = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return vectors.tolist()
