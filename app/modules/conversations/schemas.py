import uuid
from datetime import datetime
from pydantic import BaseModel


class MessageSchema(BaseModel):
    role: str
    content: str
    imgSrc: str | None = None


class ConversationCreate(BaseModel):
    title: str
    messages: list[MessageSchema] = []


class ConversationUpdate(BaseModel):
    title: str | None = None
    messages: list[MessageSchema] | None = None


class ConversationResponse(BaseModel):
    id: uuid.UUID
    title: str
    messages: list[MessageSchema]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
