from fastapi import APIRouter

from app.api.v1.routes import chat, session

api_router = APIRouter()
api_router.include_router(session.router)
api_router.include_router(chat.router)
