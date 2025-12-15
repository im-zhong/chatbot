# 2025/12/14
# zhangzhong
from chatbot.agent import get_agent
from chatbot.llm import get_chat_model
from langchain.messages import HumanMessage
import pytest

pytestmark = pytest.mark.anyio


async def test_agent() -> None:
    agent = get_agent(model=get_chat_model())

    # https://docs.langchain.com/oss/python/langgraph/streaming
    # async for chunk in agent.astream(
    #     input={"messages": [HumanMessage("please introduce lagnchain")]}
    # ):
    #     print(chunk, flush=True)

    for chunk in agent.stream(
        input={"messages": [HumanMessage("please introduce lagnchain")]},
        stream_mode="messages",
    ):
        print(chunk, sep="|", flush=True)
