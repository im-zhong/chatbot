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

# https://docs.langchain.com/oss/python/langgraph/persistence
# - The state of a thread at a particular point in time is called a checkpoint.
# - config: Config associated with this checkpoint.
# - metadata: Metadata associated with this checkpoint.
# - values: Values of the state channels at this point in time.
# - next A tuple of the node names to execute next in the graph.
# - tasks: A tuple of PregelTask objects that contain information about next tasks to be executed. If the step was previously attempted, it will include error information. If a graph was interrupted dynamically from within a node, tasks will contain additional data associated with interrupts.
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig


# 在 LangGraph 里：
# 	•	State 是在一次 graph 执行过程中持续存在的
# 	•	执行结束（到 END）后，state 就“死了”
# 	•	下一次 graph.invoke(...) → 重新创建 state
# TODO: 使用langgraph checkpointer来做跨graph调用的memory
#  只有使用 checkpointer + thread_id，state 才会跨 invoke 持久化
# TODO: 你现在每次都硬塞一个 SystemMessage：， 会导致 系统提示重复注入（如果你以后做多轮）。
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
    checkpointer = InMemorySaver()
    agent = agent_builder.compile(checkpointer=checkpointer)
    return agent


def get_config(thread_id: str = "1", user_id: str = "2") -> RunnableConfig:
    return {"configurable": {"thread_id": thread_id, "user_id": user_id}}
