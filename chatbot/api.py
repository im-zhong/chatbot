"""Docstring for chatbot.api."""

# 2025/12/14
# zhangzhong

## Authentication
# https://docs.streamlit.io/develop/concepts/connections/authentication
# https://docs.streamlit.io/develop/tutorials/authentication/google

# step 1:
# 为了用OCID，google cloud跟我要支付信息，wechat跟我要网站截图。。。
# https://open.weixin.qq.com/cgi-bin/appcreate?t=manage/createWeb&type=app&lang=zh_CN&token=9f69eada3ff04a80717b45f15db3c105eb2f5b24
# 微信的这个可以搞一下，刚好我有一个网站，用streamlit搞上玩一玩。

from __future__ import annotations


# try fastapi streaming response
# https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json
from pydantic import BaseModel
from typing_extensions import Annotated
from chatbot.llm import get_chat_model, get_embedding_model
from chatbot.agent import (
    get_agent,
    get_config,
    get_threads_for_user,
    get_all_history,
    init_new_agent_thread,
    ensure_user_threads_table,
    insert_user_thread,
)
from langchain.messages import HumanMessage
from chatbot.agent import MessagesState, DB_URI

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from contextlib import asynccontextmanager
import uuid
from chatbot.vector_store import VectorStore
from chatbot.tools import build_retrieval_tool
from langgraph.types import Command


class AgentMessage(BaseModel):
    user_id: str
    thread_id: str
    message: str
    resume: bool = False


async def agent_chat(agent, message: AgentMessage):
    # each time we call agent, we should get the snapshot of it, and resotre the messages
    # get the latest state

    # async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:
    # with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    config = get_config(
        user_id=message.user_id, thread_id=message.thread_id, resume=message.resume
    )
    # checkpoint = agent.get_state(config=config)
    # 其实需要做的事情就是把memory里面的消息放到agent的state里面吧
    # state = MessagesState(**checkpoint.values)
    # 在最开始的时候 checkpoint里面是空的
    # ！！！ 我们不需要手动管理，checkpoint会自动做persistence！！！
    # print("checkpoint: ", checkpoint)
    # if not checkpoint.values:
    #     async for chunk in agent.astream(
    #         input={"messages": [HumanMessage(message)]},
    #         stream_mode="messages",
    #         # 每次调用agent都需要传入config！
    #         # 这样才能记录聊天历史
    #         config=config,
    #     ):
    #         yield f"data: {json.dumps({'token': chunk[0].content})}\n\n"
    # else:
    #     async for chunk in agent.astream(
    #         input={"messages": checkpoint.values["messages"] + [message]},
    #         stream_mode="messages",
    #         config=config,
    #     ):
    #         yield f"data: {json.dumps({'token': chunk[0].content})}\n\n"
    # 我擦！真的！！！牛逼呀，这样就更简单了，相比于没有checkpoint的写法，实际上就只多了一个config参数而已

    # TIPS:
    # interrupt 向 graph state 注入一个 __interrupt__ 事件，然后立即停止当前 graph 执行
    # 作为一个特殊的 stream chunk 被 yield 出来
    # [token chunk]
    # [token chunk]
    # [token chunk]
    # [INTERRUPT EVENT]  ← 你必须接住
    # (stream ends)
    # https://docs.langchain.com/oss/python/langgraph/streaming#stream-multiple-modes
    # 所以必须要stream multiple modes
    # old impl
    # async for chunk in agent.astream(
    #     input={"messages": [HumanMessage(content=message.message)]},
    #     stream_mode=["messages", "events"],
    #     config=config,
    # ):
    #     yield f"data: {json.dumps({'token': chunk[0].content})}\n\n"

    # https://stackoverflow.com/questions/79582204/how-to-resume-a-langgraph-stream-after-a-custom-human-assistance-tool-interrupt
    input = {"messages": [HumanMessage(content=message.message)]}
    if message.resume:
        input = Command(resume=True)

    # new impl
    async for mode, payload in agent.astream(
        input=input,
        stream_mode=["messages", "updates"],
        config=config,
    ):
        if mode == "messages":
            msg = payload[0]
            if msg.content:
                yield f"data: {json.dumps({'type': 'token', 'token': msg.content})}\n\n"

        elif mode == "updates":
            # interrupt 就在这里
            if "__interrupt__" in payload:
                interrupt_event = payload["__interrupt__"][0]

                yield f"""data: {
                    json.dumps(
                        {
                            "type": "interrupt",
                            "id": interrupt_event.id,
                            "question": interrupt_event.value,
                        }
                    )
                }\n\n"""

                return


class UserMessage(BaseModel):
    messages: list


class NewChatRequest(BaseModel):
    user_id: str
    system_prompt: str | None = None


# 不行，看起来必须写一个fastapi lifetime span了
# https://fastapi.tiangolo.com/advanced/events


# perfect for
@asynccontextmanager
async def lifespan(app: FastAPI):
    # create async pg saver
    async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:
        await checkpointer.setup()
        await ensure_user_threads_table(checkpointer.conn)

        app.state.embeddings = get_embedding_model()

        ## create milvus client
        app.state.vector_store = VectorStore(app.state.embeddings)

        # 咱们所有的全局实例都在这里构建就对了
        llm = get_chat_model()
        # retrieval_tool = build_retrieval_tool(app.state.vector_store)
        # llm.bind_tools([retrieval_tool])

        # 需要在这里创建agent graph和checkpointer
        # 不同用户的agent用config来区分
        agent = get_agent(
            model=llm, checkpointer=checkpointer, vector_store=app.state.vector_store
        )
        app.state.agent = agent
        # get the async pgsql connector
        app.state.conn = checkpointer.conn

        yield


app = FastAPI(lifespan=lifespan)


# FastAPI streaming works internally, and clients can consume it in real time (e.g., curl -N, front-end JS fetch, Python requests with streaming, etc.)  ￼
# ❌ Swagger UI does not support streaming responses interactively or showing partial incremental chunks — it will buffer or attempt to parse the response as one complete JSON document, which fails for NDJSON/SSE.
# three way to streaming
# - curl -N
# - js EventSource for SSE
# - requests or httpx streaming iteration


async def fake_video_streamer():
    for i in range(10):
        await asyncio.sleep(1)
        yield "some fake video bytes"


some_file_path = "large-video-file.mp4"


# curl -N http://localhost:8000/
# 但是fastapi doc webpage不支持
@app.get("/")
async def main():
    return StreamingResponse(fake_video_streamer(), media_type="text/plain")


# 试一下SSE
async def generate_ndjson():
    for i in range(5):
        await asyncio.sleep(1)
        yield json.dumps({"data": i}) + "\n"


async def event_stream():
    for i in range(5):
        await asyncio.sleep(1)
        yield f"data: {json.dumps({'token': str(i)})}\n\n"


# Swagger UI is NOT a streaming client
# 我的SSE并没有chatgpt上描述的那些协议格式，就是我自己设计的json格式
# TODO：需要更加细致的学习sse的协议内容
@app.get("/sse")
def sse():
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


async def llm_chat(input: UserMessage):
    async for chunk in llm.astream(input=input.messages):
        yield f"data: {json.dumps({'token': chunk.content})}\n\n"


@app.post("/new-chat")
async def new_chat(req: NewChatRequest):
    thread_id = str(uuid.uuid4())
    await insert_user_thread(app.state.conn, req.user_id, thread_id)
    await init_new_agent_thread(
        agent=app.state.agent,
        user_id=req.user_id,
        thread_id=thread_id,
        system_prompt="let's start talk!",
    )
    return {"thread_id": thread_id}


@app.post("/chat")
def chat(input: UserMessage):
    print("get user prompt", input.model_dump())
    return StreamingResponse(
        llm_chat(input),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.post("/agent-chat")
def do_agent_chat(input: AgentMessage):
    # print("get user prompt", input.model_dump())

    # 现在的问题是interrupt怎么和streaming chat结合呢?
    # 因为需要和用户反馈，所以agent必须在适当的位置返回

    return StreamingResponse(
        agent_chat(app.state.agent, input),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.get("/all-chat-threads")
async def get_chat_history(user_id: str) -> list[str]:
    threads = await get_threads_for_user(conn=app.state.conn, user_id=user_id)
    return threads


@app.get("/thread-chat-messages")
async def get_thread_chat_messages(user_id: str, thread_id: str) -> list[dict]:
    # return {role:"", content:""}
    messages = await get_all_history(
        agent=app.state.agent, user_id=user_id, thread_id=thread_id
    )
    print(messages)
    return messages


@app.get("/new-chat")
async def get_new_chat(user_id: str) -> str:
    thread_id = str(uuid.uuid4())
    await init_new_agent_thread(
        agent=app.state.agent, user_id=user_id, thread_id=thread_id
    )
    return thread_id


# not_work
@app.get("/ndjson")
def ndjson():
    return StreamingResponse(
        generate_ndjson(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
            "Transfer-Encoding": "chunked",  # 强制分块传输
        },
    )


@app.get("/get-video")
def get_video():
    # This is the generator function. It's a "generator function" because it contains yield statements inside.
    def iterfile():  # (1)
        # By using a with block, we make sure that the file-like object is closed after the generator function is done.
        # So, after it finishes sending the response.
        with open(some_file_path, mode="rb") as file_like:  # (2)
            # This yield from tells the function to iterate over that thing named file_like.
            # And then, for each part iterated, yield that part as coming from this generator function (iterfile).
            yield from file_like  # (3)

    return StreamingResponse(iterfile(), media_type="video/mp4")
