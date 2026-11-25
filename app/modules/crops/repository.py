import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.crops.models import Crop


class CropRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, search: str | None = None) -> list[Crop]:
        q = select(Crop)
        if search:
            q = q.where(Crop.name.ilike(f"%{search}%"))
        result = await self.db.execute(q.order_by(Crop.name))
        return list(result.scalars().all())

    async def get_by_id(self, crop_id: uuid.UUID) -> Crop | None:
        result = await self.db.execute(select(Crop).where(Crop.id == crop_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Crop | None:
        result = await self.db.execute(select(Crop).where(Crop.name == name))
        return result.scalar_one_or_none()

    async def create(self, crop: Crop) -> Crop:
        self.db.add(crop)
        await self.db.flush()
        await self.db.refresh(crop)
        return crop

    async def update(self, crop: Crop) -> Crop:
        await self.db.flush()
        await self.db.refresh(crop)
        return crop

    async def delete(self, crop: Crop) -> None:
        await self.db.delete(crop)
        await self.db.flush()
