import json
from fastapi import APIRouter, Depends, File, Form, UploadFile
from app.db.session import get_db
from app.integrations.embeddings.dependencies import EmbeddingDep
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.chat.schemas import ChatMessage, ChatResponse
from app.modules.chat.service import ChatService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    embeddings: EmbeddingDep,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    message: str = Form(""),
    history: str = Form("[]"),
    image: UploadFile | None = File(None),
):
    history_list: list[ChatMessage] = [ChatMessage(**m) for m in json.loads(history or "[]")]
    image_bytes = None
    if image:
        data = await image.read()
        if data:
            image_bytes = data
    svc = ChatService(db, current_user.id, embeddings)
    return await svc.chat(message=message, history=history_list, image_bytes=image_bytes)
