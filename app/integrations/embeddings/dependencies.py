from functools import lru_cache
from typing import Annotated
from fastapi import Depends
from app.core.config import get_settings
from app.integrations.embeddings.client import EmbeddingClient


@lru_cache
def get_embedding_client() -> EmbeddingClient:
    settings = get_settings()
    return EmbeddingClient(
        model=settings.EMBEDDINGS_URL,
        embedding_dim=settings.EMBEDDING_DIM,
    )

EmbeddingDep = Annotated[EmbeddingClient, Depends(get_embedding_client)]
