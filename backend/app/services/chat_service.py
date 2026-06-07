import json
import uuid
from asyncio import CancelledError
from collections.abc import AsyncGenerator

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.message import Message, MessageRole
from app.repositories.message_repo import MessageRepository
from app.repositories.session_repo import SessionRepository
from app.services.moderation_service import ModerationService
from app.services.session_service import SessionService

SYSTEM_PROMPT = """Você é um assistente prestativo e amigável.
Regras que você deve seguir sem exceção:
- Nunca use linguagem ofensiva, palavrões ou termos inadequados.
- Não responda perguntas que contenham linguagem inapropriada.
- Seja sempre respeitoso, claro e objetivo nas respostas.
- Se não souber a resposta, diga que não sabe ao invés de inventar."""


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


class ChatService:
    def __init__(self, db: AsyncSession) -> None:
        self._message_repo = MessageRepository(db)
        self._session_service = SessionService(db)
        self._session_repo = SessionRepository(db)
        self._moderation = ModerationService()
        self._llm = ChatOllama(
            model=settings.llm_model,
            base_url=settings.ollama_base_url,
        )

    async def stream_message(
        self, session_id: uuid.UUID, user_input: str
    ) -> AsyncGenerator[str, None]:
        await self._session_service.get_session(session_id)

        user_message = await self._message_repo.create(
            session_id=session_id,
            role=MessageRole.user,
            content=user_input,
        )
        yield _sse("user_message", _serialize_message(user_message))

        if self._moderation.contains_profanity(user_input):
            full_content = self._moderation.get_violation_response()
            yield _sse("chunk", {"content": full_content})
        else:
            full_content = ""
            lc_messages = await self._build_messages(session_id)
            try:
                async for chunk in self._llm.astream(lc_messages):
                    token = str(chunk.content)
                    if token:
                        full_content += token
                        yield _sse("chunk", {"content": token})
            except CancelledError:
                pass

        assistant_message = await self._message_repo.create(
            session_id=session_id,
            role=MessageRole.assistant,
            content=full_content,
        )
        yield _sse("done", _serialize_message(assistant_message))

    async def get_history(self, session_id: uuid.UUID) -> list[Message]:
        await self._session_service.get_session(session_id)
        return await self._message_repo.list_by_session(session_id)

    async def _build_messages(self, session_id: uuid.UUID) -> list:
        history = await self._message_repo.list_by_session(session_id)
        lc_messages = [SystemMessage(content=SYSTEM_PROMPT)]
        for msg in history:
            if msg.role == MessageRole.user:
                lc_messages.append(HumanMessage(content=msg.content))
            else:
                lc_messages.append(AIMessage(content=msg.content))
        return lc_messages


def _serialize_message(msg: Message) -> dict:
    return {
        "id": str(msg.id),
        "session_id": str(msg.session_id),
        "role": msg.role,
        "content": msg.content,
        "created_at": msg.created_at.isoformat(),
    }
