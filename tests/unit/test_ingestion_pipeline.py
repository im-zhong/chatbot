from chatbot.ingest_pipeline import ingest_document
from chatbot.defs import get_testing_text
from chatbot.vector_store import VectorStore
from chatbot.llm import get_embedding_model
import pytest

pytestmark = pytest.mark.anyio


async def test_ingestion_pipeline():
    embedding = get_embedding_model()
    vector_store = VectorStore(embeddings=embedding)
    text = get_testing_text()
    await ingest_document(text=text, vector_store=vector_store)
