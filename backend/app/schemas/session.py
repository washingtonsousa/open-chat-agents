import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.agent import AgentResponse


class SessionCreate(BaseModel):
    title: str = "Nova conversa"
    agent_id: uuid.UUID | None = None


class SessionResponse(BaseModel):
    id: uuid.UUID
    title: str
    agent_id: uuid.UUID | None
    agent: AgentResponse | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SessionListResponse(BaseModel):
    sessions: list[SessionResponse]
    total: int
