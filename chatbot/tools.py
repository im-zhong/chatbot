from typing import Callable

from langchain.tools import tool
from chatbot.vector_store import VectorStore


## how to integrate retrieval into llm agent
# Agreed—two patterns, suited to different needs:
# - Retrieval as a tool (LLM decides): Keep the graph small; LLM triggers the retriever only when it thinks context is needed. Good when queries vary and you want the model to decide whether to search.
# - Retrieval as its own node (pipeline step): Always run retrieval (or run conditionally in a router). Good when every turn should be grounded, or when you want to attach fixed preprocessing/postprocessing around retrieval.


def build_retrieval_tool(vector_store: VectorStore) -> Callable:
    @tool("semantic_retrieval", return_direct=False)
    async def retrieval(query: str) -> str:
        # TIPS：工具的介绍当然要写在这个地方啦！！！！
        """Only call tool semantic_retrieval when the user explicitly mentions ‘智图·DiGraph’ or asks about that knowledge base; otherwise answer directly without tools. 注意：只有当用户提及“智图”而字时，才需要调用此工具！ 工具功能：查询智图·DiGraph 知识库：输入问题，返回最相关的段落。."""
        hits = await vector_store.semantic_search(query=query)
        return "\n\n".join(hits)

    return retrieval
