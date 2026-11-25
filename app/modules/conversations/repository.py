import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.conversations.models import Conversation

FIVE_MONTHS = timedelta(days=150)


class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, conv: Conversation) -> Conversation:
        self.db.add(conv)
        await self.db.flush()
        await self.db.refresh(conv)
        return conv

    async def get_by_id(self, conv_id: uuid.UUID, user_id: uuid.UUID) -> Conversation | None:
        result = await self.db.execute(
            select(Conversation).where(
                Conversation.id == conv_id, Conversation.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: uuid.UUID) -> list[Conversation]:
        cutoff = datetime.now(timezone.utc) - FIVE_MONTHS
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id, Conversation.updated_at >= cutoff)
            .order_by(Conversation.updated_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, conv: Conversation, title: str | None, messages: list | None) -> Conversation:
        if title is not None:
            conv.title = title
        if messages is not None:
            conv.messages = messages
        conv.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(conv)
        return conv

    async def delete(self, conv: Conversation) -> None:
        await self.db.delete(conv)
        await self.db.flush()

    async def purge_old(self, user_id: uuid.UUID) -> None:
        cutoff = datetime.now(timezone.utc) - FIVE_MONTHS
        await self.db.execute(
            delete(Conversation).where(
                Conversation.user_id == user_id, Conversation.updated_at < cutoff
            )
        )
        await self.db.flush()
