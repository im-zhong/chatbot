import types
from pathlib import Path
import sys
from unittest.mock import MagicMock

import random
import pytest
from langchain_core.documents import Document
from chatbot import vector_store
from chatbot.vector_store import VectorStore
from chatbot.llm import get_embedding_model

pytestmark = pytest.mark.anyio


class FakeEmbeddings:
    def __init__(self, dim: int = 2048) -> None:
        self.dim = dim
        self.calls: list[list[str]] = []

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(texts)
        return [[random.random() for _ in range(self.dim)] for _ in texts]


async def test_aadd_documents() -> None:
    documents = [
        Document(page_content="Alpha", metadata={"source": "notes"}),
        Document(page_content="Beta", metadata={"source": "web"}),
        Document(page_content="Gamma", metadata={"source": "pdf"}),
    ]
    # embeddings = FakeEmbeddings(dim=2048)

    # 这里应该就不能用fake embedding了 否则无法进行semantic search的测试啊

    store = VectorStore(embeddings=get_embedding_model())
    await store.aadd_documents(documents)

    # assert embeddings.calls == [[doc.page_content for doc in documents]]

    docs = store.select_documents(filter_expr="")

    # test semantic search
    hit = await store.semantic_search(query="alpha")
    print(hit[0])
    assert hit[0] == "Alpha"
