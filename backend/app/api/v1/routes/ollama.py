import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core.config import settings
from app.services.graph_service import list_bedrock_models

router = APIRouter(prefix="/models", tags=["models"])


class ModelInfo(BaseModel):
    name: str
    provider: str | None = None
    size: int | None = None


class ModelsResponse(BaseModel):
    models: list[ModelInfo]


@router.get("/ollama", response_model=ModelsResponse)
async def list_ollama_models() -> ModelsResponse:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Não foi possível conectar ao Ollama. Verifique se o serviço está rodando.",
        )

    models = [
        ModelInfo(name=m["name"], provider="ollama", size=m.get("size"))
        for m in data.get("models", [])
    ]
    return ModelsResponse(models=models)


@router.get("/bedrock", response_model=ModelsResponse)
async def list_bedrock_models_endpoint() -> ModelsResponse:
    models = list_bedrock_models()
    return ModelsResponse(
        models=[ModelInfo(name=m["name"], provider=m.get("provider")) for m in models]
    )
