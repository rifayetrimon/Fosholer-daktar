import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.modules.auth.dependencies import require_admin
from app.modules.auth.models import User
from app.modules.crops.schemas import CropCreate, CropResponse, CropUpdate
from app.modules.crops.service import CropService

router = APIRouter(prefix="/crops", tags=["crops"])


@router.get("/", response_model=list[CropResponse])
async def list_crops(search: str | None = None, db: AsyncSession = Depends(get_db)):
    svc = CropService(db)
    return await svc.list_crops(search)

@router.get("/{crop_id}", response_model=CropResponse)
async def get_crop(crop_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    svc = CropService(db)
    return await svc.get_crop(crop_id)

@router.post("/", response_model=CropResponse, status_code=status.HTTP_201_CREATED)
async def create_crop(
    data: CropCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    svc = CropService(db)
    return await svc.create_crop(data)

@router.patch("/{crop_id}", response_model=CropResponse)
async def update_crop(
    crop_id: uuid.UUID,
    data: CropUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    svc = CropService(db)
    return await svc.update_crop(crop_id, data)

@router.delete("/{crop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_crop(
    crop_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    svc = CropService(db)
    await svc.delete_crop(crop_id)
