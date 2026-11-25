import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions.error import ConflictError, NotFoundError
from app.modules.crops.models import Crop
from app.modules.crops.repository import CropRepository
from app.modules.crops.schemas import CropCreate, CropUpdate


class CropService:
    def __init__(self, db: AsyncSession):
        self.repo = CropRepository(db)

    async def list_crops(self, search: str | None = None) -> list[Crop]:
        return await self.repo.get_all(search)

    async def get_crop(self, crop_id: uuid.UUID) -> Crop:
        crop = await self.repo.get_by_id(crop_id)
        if not crop:
            raise NotFoundError("Crop not found")
        return crop

    async def create_crop(self, data: CropCreate) -> Crop:
        existing = await self.repo.get_by_name(data.name)
        if existing:
            raise ConflictError("Crop with this name already exists")
        crop = Crop(**data.model_dump())
        return await self.repo.create(crop)

    async def update_crop(self, crop_id: uuid.UUID, data: CropUpdate) -> Crop:
        crop = await self.get_crop(crop_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(crop, field, value)
        return await self.repo.update(crop)

    async def delete_crop(self, crop_id: uuid.UUID) -> None:
        crop = await self.get_crop(crop_id)
        await self.repo.delete(crop)
