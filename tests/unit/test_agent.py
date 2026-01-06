# 2025/12/14
# zhangzhong
from chatbot.agent import get_agent
from chatbot.llm import get_chat_model
from langchain.messages import HumanMessage, AIMessageChunk
from pathlib import Path
import pytest
from langgraph.checkpoint.memory import InMemorySaver
from chatbot.api import agent_chat, AgentMessage

pytestmark = pytest.mark.anyio


async def test_agent() -> None:
    agent = get_agent(model=get_chat_model(), checkpointer=InMemorySaver())

    # https://docs.langchain.com/oss/python/langgraph/streaming
    # async for chunk in agent.astream(
    #     input={"messages": [HumanMessage("please introduce lagnchain")]}
    # ):
    #     print(chunk, flush=True)

    # messages 可以流式输出llm的response
    # graph.invoke(Command(resume=True), config=config)
    # 类比推理可以得到 Command就是input
    async for chunk in agent.astream(
        input={"messages": [HumanMessage("please introduce lagnchain")]},
        stream_mode="messages",
        config={"configurable": {"user_id": "1", "thread_id": 2}},
    ):
        # chunk 本身就是一个tuple, len = 2, chunk[0]: AIMessageChunk, chunk[1]: dict
        print(chunk, sep="|", flush=True)


async def test_create_agent_graph():
    agent = get_agent(
        model=get_chat_model(), checkpointer=InMemorySaver(), vector_store={}
    )
    graph = agent.get_graph().draw_mermaid()
    print(graph)
    png_bytes = agent.get_graph().draw_mermaid_png()

    docs_dir = Path("docs")
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "agent.png").write_bytes(png_bytes)


async def test_agent_chat():
    agent = get_agent(
        model=get_chat_model(), checkpointer=InMemorySaver(), vector_store={}
    )

    agent_msg = AgentMessage(user_id="1", thread_id="2", message="介绍一下智图")

    async for msg in agent_chat(agent, agent_msg):
        # 咱们把所有的token组合起来
        print(msg)

    agent_msg = AgentMessage(user_id="1", thread_id="2", message="", resume=True)
    async for msg in agent_chat(agent, agent_msg):
        # 咱们把所有的token组合起来
        print(msg)
