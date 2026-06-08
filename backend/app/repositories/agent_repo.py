import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent


class AgentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, name: str, provider: str, llm_model: str, temperature: float, max_tokens: int | None, system_prompt: str) -> Agent:
        agent = Agent(
            name=name,
            provider=provider,
            llm_model=llm_model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
        )
        self._db.add(agent)
        await self._db.commit()
        await self._db.refresh(agent)
        return agent

    async def get_by_id(self, agent_id: uuid.UUID) -> Agent | None:
        result = await self._db.execute(select(Agent).where(Agent.id == agent_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Agent | None:
        result = await self._db.execute(select(Agent).where(Agent.name == name))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Agent]:
        result = await self._db.execute(select(Agent).order_by(Agent.created_at.desc()))
        return list(result.scalars().all())

    async def update(self, agent: Agent, **fields) -> Agent:
        for key, value in fields.items():
            if value is not None:
                setattr(agent, key, value)
        await self._db.commit()
        await self._db.refresh(agent)
        return agent

    async def delete(self, agent_id: uuid.UUID) -> bool:
        agent = await self.get_by_id(agent_id)
        if not agent:
            return False
        await self._db.delete(agent)
        await self._db.commit()
        return True
