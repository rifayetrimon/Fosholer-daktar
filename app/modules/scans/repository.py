import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.scans.models import DiseaseScan


class ScanRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, scan: DiseaseScan) -> DiseaseScan:
        self.db.add(scan)
        await self.db.flush()
        await self.db.refresh(scan)
        return scan

    async def get_by_id(self, scan_id: uuid.UUID) -> DiseaseScan | None:
        result = await self.db.execute(select(DiseaseScan).where(DiseaseScan.id == scan_id))
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        crop_name: str | None = None,
        disease: str | None = None,
    ) -> list[DiseaseScan]:
        q = select(DiseaseScan).where(DiseaseScan.user_id == user_id)
        if crop_name:
            q = q.where(DiseaseScan.crop_name.ilike(f"%{crop_name}%"))
        if disease:
            q = q.where(DiseaseScan.predicted_disease.ilike(f"%{disease}%"))
        result = await self.db.execute(q.order_by(DiseaseScan.created_at.desc()))
        return list(result.scalars().all())

    async def list_all(
        self,
        crop_name: str | None = None,
        disease: str | None = None,
    ) -> list[DiseaseScan]:
        q = select(DiseaseScan)
        if crop_name:
            q = q.where(DiseaseScan.crop_name.ilike(f"%{crop_name}%"))
        if disease:
            q = q.where(DiseaseScan.predicted_disease.ilike(f"%{disease}%"))
        result = await self.db.execute(q.order_by(DiseaseScan.created_at.desc()))
        return list(result.scalars().all())

    async def delete(self, scan: DiseaseScan) -> None:
        await self.db.delete(scan)
        await self.db.flush()
