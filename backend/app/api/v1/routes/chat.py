import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.chat import ChatHistoryResponse, ChatRequest, MessageResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/stream")
async def stream_message(
    payload: ChatRequest, db: AsyncSession = Depends(get_db)
) -> StreamingResponse:
    service = ChatService(db)
    return StreamingResponse(
        service.stream_message(session_id=payload.session_id, user_input=payload.message),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/{session_id}/history", response_model=ChatHistoryResponse)
async def get_history(
    session_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> ChatHistoryResponse:
    service = ChatService(db)
    messages = await service.get_history(session_id)
    return ChatHistoryResponse(
        session_id=session_id,
        messages=[MessageResponse.model_validate(m) for m in messages],
    )
