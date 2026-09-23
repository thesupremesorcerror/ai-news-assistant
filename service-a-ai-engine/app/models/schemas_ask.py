"""
schemas_ask.py
--------------
Pydantic models for the RAG query endpoint (POST /api/ask).
Kept in a separate module from the ingestion schemas so each
endpoint's contract can evolve independently.
"""

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1, examples=["What did the RBI decide about interest rates?"])
    top_k: int = Field(3, ge=1, le=10, description="Number of semantic matches to retrieve from Qdrant")


class RetrievedChunk(BaseModel):
    title: str
    content_chunk: str
    source_url: str
    published_date: str
    score: float


class AskResponse(BaseModel):
    query: str
    answer: str
    sources: list[str]
    retrieved_chunks: list[RetrievedChunk]
