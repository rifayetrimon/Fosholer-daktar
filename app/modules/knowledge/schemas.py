import uuid
from datetime import datetime
from pydantic import BaseModel


class KnowledgeIngestRequest(BaseModel):
    disease_name: str
    crop_name: str
    content: str
    source: str | None = None

class KnowledgeResponse(BaseModel):
    id: uuid.UUID
    disease_name: str
    crop_name: str
    content: str
    source: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
