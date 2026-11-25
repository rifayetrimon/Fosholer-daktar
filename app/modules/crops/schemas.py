import uuid
from datetime import datetime
from pydantic import BaseModel


class CropCreate(BaseModel):
    name: str
    description: str | None = None


class CropUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class CropResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
