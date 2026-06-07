import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.agent import AgentCreate, AgentListResponse, AgentResponse, AgentUpdate
from app.services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    payload: AgentCreate, db: AsyncSession = Depends(get_db)
) -> AgentResponse:
    service = AgentService(db)
    agent = await service.create_agent(payload)
    return AgentResponse.model_validate(agent)


@router.get("/", response_model=AgentListResponse)
async def list_agents(db: AsyncSession = Depends(get_db)) -> AgentListResponse:
    service = AgentService(db)
    agents = await service.list_agents()
    return AgentListResponse(
        agents=[AgentResponse.model_validate(a) for a in agents],
        total=len(agents),
    )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> AgentResponse:
    service = AgentService(db)
    agent = await service.get_agent(agent_id)
    return AgentResponse.model_validate(agent)


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: uuid.UUID, payload: AgentUpdate, db: AsyncSession = Depends(get_db)
) -> AgentResponse:
    service = AgentService(db)
    agent = await service.update_agent(agent_id, payload)
    return AgentResponse.model_validate(agent)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> None:
    service = AgentService(db)
    await service.delete_agent(agent_id)
