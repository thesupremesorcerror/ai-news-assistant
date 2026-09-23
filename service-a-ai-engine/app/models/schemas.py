"""
schemas.py
----------
Pydantic models describing the shape of data flowing in/out of the
ingestion API. Keeping these separate from the Qdrant payload format
lets the two evolve independently.
"""

from datetime import date
from pydantic import BaseModel, Field, HttpUrl


class NewsArticleIn(BaseModel):
    """A single raw news article as submitted by a client for ingestion."""

    title: str = Field(..., min_length=1, examples=["RBI Holds Repo Rate Steady"])
    content: str = Field(..., min_length=1, description="Full article body text")
    source_url: HttpUrl
    published_date: date


class IngestRequest(BaseModel):
    """Payload for POST /api/ingest — a batch of articles to embed & store."""

    articles: list[NewsArticleIn] = Field(..., min_length=1)


class IngestResultItem(BaseModel):
    article_title: str
    chunks_created: int
    point_ids: list[str]


class IngestResponse(BaseModel):
    status: str
    collection: str
    total_articles: int
    total_chunks_upserted: int
    results: list[IngestResultItem]
