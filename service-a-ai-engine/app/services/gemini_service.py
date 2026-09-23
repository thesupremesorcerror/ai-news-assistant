"""
gemini_service.py
------------------
Wraps google-generativeai so the rest of the app only deals with
"give me a query + context, get an answer back" — no SDK details
leak into the route/orchestration layer.
"""

import logging

import google.generativeai as genai
from fastapi import HTTPException, status

from app.core.config import get_settings
from app.models.schemas_ask import RetrievedChunk

logger = logging.getLogger("nemesis_news.gemini")

settings = get_settings()

_GENAI_CONFIGURED = False

GEMINI_MODEL_NAME = "gemini-3.6-flash"

PROMPT_TEMPLATE = (
    "You are a news assistant. Answer the question using ONLY the "
    "provided context. If the context does not contain the answer, "
    "say you don't know.\n\n"
    "Context:\n{context}\n\n"
    "Question: {query}"
)


def _configure_genai() -> None:
    """Configure the google-generativeai SDK exactly once per process."""
    global _GENAI_CONFIGURED
    if _GENAI_CONFIGURED:
        return

    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GEMINI_API_KEY is not configured. Set it in your .env file.",
        )

    genai.configure(api_key=settings.GEMINI_API_KEY)
    _GENAI_CONFIGURED = True


def build_augmented_prompt(query: str, chunks: list[RetrievedChunk]) -> str:
    """
    Assemble the RAG prompt from retrieved chunks. Each chunk is
    labeled with its source title so the model (and a human reading
    logs) can trace which snippet came from where.
    """
    if not chunks:
        context = "No relevant context was found in the news database."
    else:
        context = "\n\n".join(
            f"[Source: {chunk.title}]\n{chunk.content_chunk}" for chunk in chunks
        )

    return PROMPT_TEMPLATE.format(context=context, query=query)


def generate_answer(prompt: str) -> str:
    """Send the augmented prompt to Gemini and return the plain-text answer."""
    _configure_genai()

    try:
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        response = model.generate_content(prompt)
    except Exception as exc:
        logger.exception("Gemini generation failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gemini API call failed: {exc}",
        ) from exc

    answer_text = getattr(response, "text", None)
    if not answer_text:
        logger.warning("Gemini returned an empty response for prompt.")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Gemini returned an empty response.",
        )

    return answer_text.strip()
