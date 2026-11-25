import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.knowledge.models import DiseaseKnowledge


class KnowledgeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, item: DiseaseKnowledge) -> DiseaseKnowledge:
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def search_similar(
        self, embedding: list[float], limit: int = 5
    ) -> list[DiseaseKnowledge]:
        result = await self.db.execute(
            select(DiseaseKnowledge)
            .where(DiseaseKnowledge.embedding.isnot(None))
            .order_by(DiseaseKnowledge.embedding.cosine_distance(embedding))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_all(self, disease_name: str | None = None) -> list[DiseaseKnowledge]:
        q = select(DiseaseKnowledge)
        if disease_name:
            q = q.where(DiseaseKnowledge.disease_name.ilike(f"%{disease_name}%"))
        result = await self.db.execute(q.order_by(DiseaseKnowledge.disease_name))
        return list(result.scalars().all())

    async def get_by_disease(self, disease_name: str) -> list[DiseaseKnowledge]:
        result = await self.db.execute(
            select(DiseaseKnowledge).where(
                DiseaseKnowledge.disease_name.ilike(f"%{disease_name}%")
            )
        )
        return list(result.scalars().all())
