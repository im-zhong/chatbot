from chatbot.tools import build_retrieval_tool
from chatbot.vector_store import VectorStore
from chatbot.llm import get_embedding_model, get_chat_model


def test_retrieval_tool():
    embedding = get_embedding_model()
    vector_store = VectorStore(embeddings=embedding)

    tool = build_retrieval_tool(vector_store=vector_store)

    llm = get_chat_model()
    # TIPS: llm.bind_tools并没有mutatellm，所以绑定之后要重新赋值
    llm = llm.bind_tools([tool])

    # invoke一次，只会触发一次工具调用，如果是自己手动写的话，需要把工具的调用的返回值拼接，再进行一次大模型的调用才行
    # TODO：仔细的看看langgraph和tool是怎么结合的？
    # oooooooo! 就算是在langgraph里面 tool node也是要自己写的 OK！
    print(llm.invoke("介绍智图DiGraph"))
