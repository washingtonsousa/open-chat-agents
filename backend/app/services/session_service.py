import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session
from app.repositories.session_repo import SessionRepository


class SessionService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = SessionRepository(db)

    async def create_session(self, title: str = "Nova conversa", agent_id: uuid.UUID | None = None) -> Session:
        return await self._repo.create(title=title, agent_id=agent_id)

    async def get_session(self, session_id: uuid.UUID) -> Session:
        session = await self._repo.get_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sessão {session_id} não encontrada.",
            )
        return session

    async def list_sessions(self) -> list[Session]:
        return await self._repo.list_all()

    async def delete_session(self, session_id: uuid.UUID) -> None:
        deleted = await self._repo.delete(session_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sessão {session_id} não encontrada.",
            )
