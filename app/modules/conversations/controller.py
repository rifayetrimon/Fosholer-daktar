import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions.error import NotFoundError
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.conversations.models import Conversation
from app.modules.conversations.repository import ConversationRepository
from app.modules.conversations.schemas import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("/", response_model=list[ConversationResponse])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = ConversationRepository(db)
    await repo.purge_old(current_user.id)
    return await repo.list_by_user(current_user.id)




@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    body: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = ConversationRepository(db)
    conv = Conversation(
        user_id=current_user.id,
        title=body.title,
        messages=[m.model_dump() for m in body.messages],
    )
    return await repo.create(conv)

@router.put("/{conv_id}", response_model=ConversationResponse)
async def update_conversation(
    conv_id: uuid.UUID,
    body: ConversationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = ConversationRepository(db)
    conv = await repo.get_by_id(conv_id, current_user.id)
    if not conv:
        raise NotFoundError("Conversation not found")
    messages = [m.model_dump() for m in body.messages] if body.messages is not None else None
    return await repo.update(conv, body.title, messages)

@router.delete("/{conv_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conv_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = ConversationRepository(db)
    conv = await repo.get_by_id(conv_id, current_user.id)
    if not conv:
        raise NotFoundError("Conversation not found")
    await repo.delete(conv)
