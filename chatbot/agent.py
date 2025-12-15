# 2025/12/14
# zhangzhong
# https://docs.langchain.com/oss/python/langgraph/quickstart

from langchain.messages import SystemMessage, AnyMessage
from langgraph.graph.state import CompiledStateGraph
from typing_extensions import Annotated, TypedDict, Any
from operator import add
from langgraph.graph import StateGraph, START, END
from langchain_core.language_models import BaseChatModel
from chatbot.llm import get_chat_model


class MessagesState(TypedDict):
    # reducer: The Annotated type with operator.add ensures that new messages are appended to the existing list rather than replacing it.
    messages: Annotated[list[AnyMessage], add]
    llm_calls: int


def get_agent(
    model: BaseChatModel,
) -> CompiledStateGraph[MessagesState, None, MessagesState, MessagesState]:
    def llm_call(state: dict) -> dict[str, Any]:
        """LLM decides whether to call a tool or not"""


        

        return {
            "messages": [
                model.invoke(
                    [SystemMessage(content="You are a helpful chatbot.")]
                    + state["messages"]
                )
            ],
            "llm_calls": state.get("llm_calls", 0) + 1,
        }

    # 这里应该有两个东西
    # State: State in LangGraph persists throughout the agent’s execution
    # Context: 暂时还没有学到

    # Build workflow
    agent_builder = StateGraph(state_schema=MessagesState)

    # Add nodes, 支持clouser
    agent_builder.add_node("llm_call", llm_call)

    # Add edges to connect nodes
    agent_builder.add_edge(START, "llm_call")
    agent_builder.add_edge("llm_call", END)

    # Compile the agent
    agent = agent_builder.compile()
    return agent
