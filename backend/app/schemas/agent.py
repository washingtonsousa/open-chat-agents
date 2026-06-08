import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class AgentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    provider: str = Field(default="ollama", pattern="^(ollama|bedrock)$")
    llm_model: str = Field(min_length=1, max_length=100)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, gt=0)
    system_prompt: str = Field(min_length=1)

    @field_validator("name")
    @classmethod
    def name_strip(cls, v: str) -> str:
        return v.strip()


class AgentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    provider: str | None = Field(default=None, pattern="^(ollama|bedrock)$")
    llm_model: str | None = Field(default=None, min_length=1, max_length=100)
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, gt=0)
    system_prompt: str | None = Field(default=None, min_length=1)


class AgentResponse(BaseModel):
    id: uuid.UUID
    name: str
    provider: str
    llm_model: str
    temperature: float
    max_tokens: int | None
    system_prompt: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AgentListResponse(BaseModel):
    agents: list[AgentResponse]
    total: int
