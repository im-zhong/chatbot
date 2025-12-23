# chatbot

A simple chatbot

## Start FastAPI Server

`uv run uvicorn --reload chatbot.api:app`

## Start Streamlit APP

- When passing your script some custom arguments, they must be passed after two dashes.
- Otherwise the arguments get interpreted as arguments to Streamlit itself.
- use  [-- script args] to pass args to your script

`PYTHONPATH=. uv run streamlit run chatbot/app/app.py`

- start the multi page app
`PYTHONPATH=. uv run streamlit run`

### 1. How to debug streamlit?

1. `python -m streamlit run your_script.py` cause streamlit could be start as a normal python module, so I think just configure it in the vscode debug conf, and start it as a normal python program, then you could debug it.

### TODO

1. use milvus with BGE

✔ Best all-around BGE model for RAG: BAAI/bge-m3
✔ Why it’s best: Unified dense + sparse + multi-vector retrieval + strong multilingual performance.  ￼
✔ Pairs well with: BGE rerankers to boost precision

- <https://huggingface.co/BAAI/bge-m3>
- some suggestions for BGE-M3
- proper way to use pymilvus with lang graph is just use a function tool or a node to wrap it, it is very easy, and work!

Got it — LangGraph + pymilvus + BGE is a totally normal stack, and you don’t need the LangChain Milvus integration to be “proper”.

What’s the proper way?

In LangGraph, the “proper” way is:

 1. Build a clean, library-agnostic retriever module (pymilvus + BGE embed + formatting).
 2. Use it in LangGraph as either:

 • a node function (for deterministic RAG graphs), or
 • a Tool (if you’re doing agent-style tool calling).

You only implement langchain_core.retrievers.BaseRetriever if you want compatibility with LangChain components that expect it (e.g., create_retrieval_chain, RetrievalQA, some reranker wrappers, etc.). LangGraph itself does not require it.

⸻

Recommended architecture (best of both worlds)

1) Core retriever (no LangChain dependency)

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass
class Chunk:
    text: str
    score: float
    metadata: Dict[str, Any]

class MilvusBGERetriever:
    def __init__(
        self,
        collection,
        embed_query_fn,
        anns_field: str = "embedding",
        text_field: str = "text",
        output_fields: Optional[List[str]] = None,
        search_params: Optional[dict] = None,
    ):
        self.collection = collection
        self.embed_query_fn = embed_query_fn
        self.anns_field = anns_field
        self.text_field = text_field
        self.output_fields = output_fields or [text_field, "doc_id", "source"]
        self.search_params = search_params or {"metric_type": "COSINE", "params": {"ef": 64}}

    def retrieve(self, query: str, top_k: int = 8, expr: Optional[str] = None) -> List[Chunk]:
        qvec = self.embed_query_fn(query)  # BGE query embedding -> List[float]
        res = self.collection.search(
            data=[qvec],
            anns_field=self.anns_field,
            param=self.search_params,
            limit=top_k,
            expr=expr,
            output_fields=self.output_fields,
        )

        out: List[Chunk] = []
        for hit in res[0]:
            ent = hit.entity
            out.append(
                Chunk(
                    text=ent.get(self.text_field),
                    score=float(hit.score),
                    metadata={k: ent.get(k) for k in self.output_fields if k != self.text_field},
                )
            )
        return out

2A) Use as a LangGraph node (most common for RAG)

def retrieve_node(state):
    query = state["question"]
    chunks = state["retriever"].retrieve(query, top_k=8)
    state["context"] = "\n\n".join([c.text for c in chunks])
    state["sources"] = [c.metadata for c in chunks]
    return state

2B) Use as an agent Tool (when the model chooses to retrieve)

If you’re using tool-calling in LangGraph, wrap it:

def milvus_search_tool(query: str, top_k: int = 8) -> dict:
    chunks = retriever.retrieve(query, top_k=top_k)
    return {
        "chunks": [{"text": c.text, "score": c.score, "metadata": c.metadata} for c in chunks]
    }

This is “proper” because your retrieval logic stays stable and testable, and LangGraph just consumes it.

⸻

When should you implement BaseRetriever too?

Do it only if you want to plug into LangChain-style components that expect Document objects.

You can add a thin adapter on top of your core retriever:

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

class LCAdapterRetriever(BaseRetriever):
    def __init__(self, core: MilvusBGERetriever):
        self.core = core

    def _get_relevant_documents(self, query: str, *, run_manager=None):
        chunks = self.core.retrieve(query)
        return [Document(page_content=c.text, metadata={**c.metadata, "score": c.score}) for c in chunks]

This way:
 • Core retriever stays pymilvus+BGE-only ✅
 • You can still interop with LangChain bits when convenient ✅

⸻

My recommendation for your setup

Since you’re on LangGraph, I’d do:
 • Core retriever + LangGraph node (default path)
 • Add a Tool wrapper only if you’re doing agent tool-selection
 • Add BaseRetriever adapter only if you specifically need LangChain retriever APIs

If you show me your current LangGraph style (Functional API vs Graph API, and whether you use tool-calling), I can sketch the cleanest graph wiring pattern (state schema + nodes + where to store retriever/collection).

既然如此，那么可以先不用BGE，先用milvus做一个最简单的向量数据库，embedding用api来做，然后做成一个agent的tool
然后再加上BGE-M3，这样的顺序来。
