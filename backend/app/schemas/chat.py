import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator

from app.models.message import MessageRole


class MessageResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    role: MessageRole
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    session_id: uuid.UUID
    message: str

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("A mensagem não pode estar vazia.")
        return v.strip()


class ChatResponse(BaseModel):
    session_id: uuid.UUID
    user_message: MessageResponse
    assistant_message: MessageResponse


class ChatHistoryResponse(BaseModel):
    session_id: uuid.UUID
    messages: list[MessageResponse]
