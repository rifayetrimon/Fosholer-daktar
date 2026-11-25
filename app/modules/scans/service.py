import uuid
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions.error import ForbiddenError, NotFoundError
from app.ml.classifier import classify_disease
from app.modules.scans.models import DiseaseScan
from app.modules.scans.repository import ScanRepository


class ScanService:
    def __init__(self, db: AsyncSession):
        self.repo = ScanRepository(db)

    async def create_scan(
        self, user_id: uuid.UUID, file: UploadFile, notes: str | None = None
    ) -> DiseaseScan:
        image_bytes = await file.read()
        result = await classify_disease(image_bytes)

        disease_label = result["label"]
        parts = disease_label.split("___")
        crop_name = parts[0] if len(parts) > 1 else "Unknown"

        scan = DiseaseScan(
            user_id=user_id,
            crop_name=crop_name,
            predicted_disease=disease_label,
            confidence=result["confidence"],
            notes=notes,
        )
        return await self.repo.create(scan)

    async def list_scans(
        self,
        user_id: uuid.UUID,
        is_admin: bool,
        crop_name: str | None,
        disease: str | None,
    ) -> list[DiseaseScan]:
        if is_admin:
            return await self.repo.list_all(crop_name, disease)
        return await self.repo.list_by_user(user_id, crop_name, disease)

    async def get_scan(
        self, scan_id: uuid.UUID, user_id: uuid.UUID, is_admin: bool
    ) -> DiseaseScan:
        scan = await self.repo.get_by_id(scan_id)
        if not scan:
            raise NotFoundError("Scan not found")
        if not is_admin and scan.user_id != user_id:
            raise ForbiddenError()
        return scan

    async def delete_scan(
        self, scan_id: uuid.UUID, user_id: uuid.UUID, is_admin: bool
    ) -> None:
        scan = await self.get_scan(scan_id, user_id, is_admin)
        await self.repo.delete(scan)
