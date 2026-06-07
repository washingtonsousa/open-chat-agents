import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message, MessageRole


class MessageRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, session_id: uuid.UUID, role: MessageRole, content: str) -> Message:
        message = Message(session_id=session_id, role=role, content=content)
        self._db.add(message)
        await self._db.commit()
        await self._db.refresh(message)
        return message

    async def list_by_session(self, session_id: uuid.UUID) -> list[Message]:
        result = await self._db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
        )
        return list(result.scalars().all())
