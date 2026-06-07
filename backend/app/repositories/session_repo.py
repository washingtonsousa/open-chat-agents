import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.session import Session


class SessionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, title: str, agent_id: uuid.UUID | None = None) -> Session:
        session = Session(title=title, agent_id=agent_id)
        self._db.add(session)
        await self._db.commit()
        return await self.get_by_id(session.id)

    async def get_by_id(self, session_id: uuid.UUID) -> Session | None:
        result = await self._db.execute(
            select(Session)
            .where(Session.id == session_id)
            .options(selectinload(Session.messages), selectinload(Session.agent))
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Session]:
        result = await self._db.execute(
            select(Session)
            .options(selectinload(Session.agent))
            .order_by(Session.updated_at.desc())
        )
        return list(result.scalars().all())

    async def delete(self, session_id: uuid.UUID) -> bool:
        session = await self.get_by_id(session_id)
        if not session:
            return False
        await self._db.delete(session)
        await self._db.commit()
        return True
