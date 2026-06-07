import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter(prefix="/ollama", tags=["ollama"])


class OllamaModel(BaseModel):
    name: str
    size: int | None = None


class OllamaModelsResponse(BaseModel):
    models: list[OllamaModel]


@router.get("/models", response_model=OllamaModelsResponse)
async def list_models() -> OllamaModelsResponse:
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
        OllamaModel(name=m["name"], size=m.get("size"))
        for m in data.get("models", [])
    ]
    return OllamaModelsResponse(models=models)
