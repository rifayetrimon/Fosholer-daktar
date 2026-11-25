from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatResponse(BaseModel):
    reply: str
    sources_used: bool = False
    disease_detected: str | None = None
    confidence: float | None = None
