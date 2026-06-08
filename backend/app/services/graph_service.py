from collections.abc import AsyncGenerator

import boto3
from langchain_aws import ChatBedrock
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, MessagesState, StateGraph

from app.core.config import settings
from app.models.agent import Agent, LLMProvider


def _build_llm(agent: Agent) -> BaseChatModel:
    if agent.provider == LLMProvider.bedrock:
        kwargs: dict = {
            "model_id": agent.llm_model,
            "region_name": settings.aws_region,
            "model_kwargs": {
                "temperature": agent.temperature,
                **({"max_tokens": agent.max_tokens} if agent.max_tokens else {}),
            },
        }
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            kwargs["credentials"] = {
                "access_key": settings.aws_access_key_id,
                "secret_key": settings.aws_secret_access_key,
            }
        return ChatBedrock(**kwargs)

    return ChatOllama(
        model=agent.llm_model,
        temperature=agent.temperature,
        base_url=settings.ollama_base_url,
        **({"num_predict": agent.max_tokens} if agent.max_tokens else {}),
    )


def _build_graph(agent: Agent):
    llm = _build_llm(agent)

    def chat_node(state: MessagesState) -> dict:
        response = llm.invoke(state["messages"])
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("chat", chat_node)
    builder.set_entry_point("chat")
    builder.add_edge("chat", END)
    return builder.compile()


async def stream_graph(agent: Agent, messages: list[BaseMessage]) -> AsyncGenerator[str, None]:
    graph = _build_graph(agent)
    async for event in graph.astream_events({"messages": messages}, version="v2"):
        if event["event"] == "on_chat_model_stream":
            token: str = event["data"]["chunk"].content
            if token:
                yield token


def list_bedrock_models() -> list[dict]:
    kwargs: dict = {"region_name": settings.aws_region}
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        kwargs["aws_access_key_id"] = settings.aws_access_key_id
        kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

    try:
        client = boto3.client("bedrock", **kwargs)
        response = client.list_foundation_models(byOutputModality="TEXT")
        return [
            {
                "name": m["modelId"],
                "provider": m.get("providerName", ""),
                "input_modalities": m.get("inputModalities", []),
            }
            for m in response.get("modelSummaries", [])
            if m.get("modelLifecycle", {}).get("status") == "ACTIVE"
        ]
    except Exception:
        return []
