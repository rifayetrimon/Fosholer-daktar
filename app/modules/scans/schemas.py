import uuid
from datetime import datetime
from pydantic import BaseModel


class ScanResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    crop_name: str
    predicted_disease: str
    confidence: float
    treatment_advice: str | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
