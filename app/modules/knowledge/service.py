import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.integrations.embeddings.client import EmbeddingClient
from app.modules.knowledge.document_parser import chunk_text, extract_text
from app.modules.knowledge.models import DiseaseKnowledge
from app.modules.knowledge.repository import KnowledgeRepository
from app.modules.knowledge.schemas import KnowledgeIngestRequest



logger = logging.getLogger("uvicorn.error")


class KnowledgeService:
    def __init__(self, db: AsyncSession, embedding_client: EmbeddingClient) -> None:
        self.repo = KnowledgeRepository(db)
        self.embeddings = embedding_client

    async def ingest(self, data: KnowledgeIngestRequest) -> DiseaseKnowledge:
        embedding = await self.embeddings.embed_document(data.disease_name, data.content)
        item = DiseaseKnowledge(
            disease_name=data.disease_name,
            crop_name=data.crop_name,
            content=data.content,
            source=data.source,
            embedding=embedding,
        )
        return await self.repo.create(item)

    async def search_relevant(self, query: str, limit: int = 5) -> list[DiseaseKnowledge]:
        try:
            query_embedding = await self.embeddings.embed_query(query)
            return await self.repo.search_similar(query_embedding, limit)
        except Exception as exc:
            logger.error("Knowledge search failed [%s]: %s", type(exc).__name__, exc, exc_info=True)
            try:
                await self.repo.db.rollback()
            except Exception as rb_exc:
                logger.error("Rollback also failed: %s", rb_exc)
            return []

    async def ingest_document(
        self,
        file_bytes: bytes,
        filename: str,
        disease_name: str,
        crop_name: str,
        source: str | None = None,
    ) -> list[DiseaseKnowledge]:
        raw_text = extract_text(file_bytes, filename)
        chunks = chunk_text(raw_text)
        results = []
        for i, chunk in enumerate(chunks):
            req = KnowledgeIngestRequest(
                disease_name=f"{disease_name}_chunk_{i + 1}",
                crop_name=crop_name,
                content=chunk,
                source=source or filename,
            )
            item = await self.ingest(req)
            results.append(item)
        return results

    async def list_knowledge(self, disease_name: str | None = None) -> list[DiseaseKnowledge]:
        return await self.repo.get_all(disease_name)
