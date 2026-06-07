from collections.abc import AsyncGenerator

from langchain_core.messages import BaseMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, MessagesState, StateGraph

from app.core.config import settings
from app.models.agent import Agent


def _build_graph(agent: Agent):
    llm = ChatOllama(
        model=agent.llm_model,
        temperature=agent.temperature,
        base_url=settings.ollama_base_url,
        **({"num_predict": agent.max_tokens} if agent.max_tokens else {}),
    )

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
