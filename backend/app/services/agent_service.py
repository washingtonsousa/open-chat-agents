import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent
from app.repositories.agent_repo import AgentRepository
from app.schemas.agent import AgentCreate, AgentUpdate


class AgentService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = AgentRepository(db)

    async def create_agent(self, payload: AgentCreate) -> Agent:
        existing = await self._repo.get_by_name(payload.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Já existe um agente com o nome '{payload.name}'.",
            )
        return await self._repo.create(
            name=payload.name,
            provider=payload.provider,
            llm_model=payload.llm_model,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
            system_prompt=payload.system_prompt,
        )

    async def get_agent(self, agent_id: uuid.UUID) -> Agent:
        agent = await self._repo.get_by_id(agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agente {agent_id} não encontrado.",
            )
        return agent

    async def list_agents(self) -> list[Agent]:
        return await self._repo.list_all()

    async def update_agent(self, agent_id: uuid.UUID, payload: AgentUpdate) -> Agent:
        agent = await self.get_agent(agent_id)
        updates = payload.model_dump(exclude_none=True)
        if "name" in updates and updates["name"] != agent.name:
            existing = await self._repo.get_by_name(updates["name"])
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Já existe um agente com o nome '{updates['name']}'.",
                )
        return await self._repo.update(agent, **updates)

    async def delete_agent(self, agent_id: uuid.UUID) -> None:
        deleted = await self._repo.delete(agent_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agente {agent_id} não encontrado.",
            )
