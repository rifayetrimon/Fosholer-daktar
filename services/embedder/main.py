"""Lightweight embedding microservice backed by the Gemini embedding API."""
import os
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai

logger = logging.getLogger("uvicorn.error")

app = FastAPI(title="Embedding Service")

_client: genai.Client | None = None
MODEL = os.environ.get("EMBEDDINGS_MODEL", "gemini-embedding-001")


def get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")
        _client = genai.Client(api_key=api_key)
    return _client


class EmbedRequest(BaseModel):
    text: str


class EmbedResponse(BaseModel):
    embedding: list[float]


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/embed", response_model=EmbedResponse)
async def embed(req: EmbedRequest):
    try:
        client = get_client()
        response = await client.aio.models.embed_content(model=MODEL, contents=req.text)
        return EmbedResponse(embedding=response.embeddings[0].values)
    except Exception as e:
        logger.error("Embedding failed: %s", e)
        raise HTTPException(status_code=500, detail="Embedding failed")
