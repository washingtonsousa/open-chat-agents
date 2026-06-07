from fastapi import APIRouter

from app.api.v1.routes import agent, chat, ollama, session

api_router = APIRouter()
api_router.include_router(session.router)
api_router.include_router(chat.router)
api_router.include_router(agent.router)
api_router.include_router(ollama.router)
