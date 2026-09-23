"""
main.py
-------
FastAPI application entrypoint for Service A (AI Engine).

Run with:
    uvicorn app.main:app --reload --port 8000
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.qdrant_client import ensure_collection_exists
from app.routes import ask, ingest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nemesis_news.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: make sure Qdrant is reachable and the collection exists
    # before we accept traffic.
    try:
        ensure_collection_exists()
    except Exception:
        logger.exception(
            "Could not verify/create Qdrant collection on startup. "
            "Is Qdrant running at the configured QDRANT_URL?"
        )
    yield
    # Shutdown: nothing to clean up yet.


app = FastAPI(
    title="AI-Powered Conversational News Assistant — AI Engine",
    description="Service A: embeddings, vector search (Qdrant) and RAG/Gemini LLM.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    logger.exception("Unhandled exception on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Check server logs for details."},
    )


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "ai-engine"}


app.include_router(ingest.router)
app.include_router(ask.router)
