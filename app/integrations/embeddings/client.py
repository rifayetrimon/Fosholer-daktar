import logging
import time
import httpx
from google import genai
from app.core.config import get_settings

logger = logging.getLogger("uvicorn.error")


class EmbeddingClient:
    def __init__(self, model: str, embedding_dim: int) -> None:
        self.model = model
        self.embedding_dim = embedding_dim
        self._genai_client: genai.Client | None = None
        self._use_http = model.startswith("http://") or model.startswith("https://")

    def _get_genai(self) -> genai.Client:
        if self._genai_client is None:
            self._genai_client = genai.Client(
                api_key=get_settings().GEMINI_API_KEY.get_secret_value()
            )
        return self._genai_client

    async def _embed_via_http(self, text: str) -> list[float]:
        url = self.model.rstrip("/") + "/embed"
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(url, json={"text": text})
            r.raise_for_status()
            return r.json()["embedding"]

    async def _embed_via_genai(self, text: str) -> list[float]:
        response = await self._get_genai().aio.models.embed_content(
            model=self.model,
            contents=text,
        )
        return response.embeddings[0].values

    async def embed(self, text: str) -> list[float]:
        preview = text[:80].replace("\n", " ")
        dots = "..." if len(text) > 80 else ""
        logger.info(f'[embedding] -> "{preview}{dots}"')
        started = time.perf_counter()

        vector = (
            await self._embed_via_http(text)
            if self._use_http
            else await self._embed_via_genai(text)
        )

        ms = (time.perf_counter() - started) * 1000
        first = ", ".join(str(round(n, 4)) for n in vector[:5])
        logger.info(f"[embedding] <- {len(vector)} dims [{first}, ...] in {ms:.0f} ms")
        return vector

    async def embed_query(self, question: str) -> list[float]:
        return await self.embed(question)

    async def embed_document(self, title: str, text: str) -> list[float]:
        return await self.embed(f"{title}: {text}")
