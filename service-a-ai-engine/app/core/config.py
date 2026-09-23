"""
config.py
---------
Centralized application configuration. Loads values from a .env file
(via pydantic-settings) so secrets and environment-specific values
(Qdrant URL, Gemini API key, etc.) are never hardcoded.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Qdrant Vector DB ---
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION_NAME: str = "news_embeddings"

    # --- Embedding model ---
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # --- Gemini LLM (used from Phase 2 onward) ---
    GEMINI_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings accessor so we parse .env only once per process
    and can still override it in tests via dependency-injection.
    """
    return Settings()
