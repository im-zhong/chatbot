from chatbot.llm import get_embedding_model
from chatbot.splitter import get_chinese_splitter
from chatbot.vector_store import VectorStore


async def ingest_document(text: str, vector_store: VectorStore):
    embedding = get_embedding_model()

    # first, split the text
    splitter = get_chinese_splitter()
    documents = splitter.create_documents([text])

    # then, use embedding model to embed all these documents
    await vector_store.aadd_documents(documents=documents)
