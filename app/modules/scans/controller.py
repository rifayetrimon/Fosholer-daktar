import uuid
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.scans.schemas import ScanResponse
from app.modules.scans.service import ScanService

router = APIRouter(prefix="/scans", tags=["scans"])


@router.post("/", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(
    file: UploadFile = File(...),
    notes: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = ScanService(db)
    return await svc.create_scan(current_user.id, file, notes)


@router.get("/", response_model=list[ScanResponse])
async def list_scans(
    crop_name: str | None = None,
    disease: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = ScanService(db)
    return await svc.list_scans(current_user.id, current_user.role == "admin", crop_name, disease)


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = ScanService(db)
    return await svc.get_scan(scan_id, current_user.id, current_user.role == "admin")


@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan(
    scan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = ScanService(db)
    await svc.delete_scan(scan_id, current_user.id, current_user.role == "admin")
