"""Docstring for chatbot.api."""

# 2025/12/14
# zhangzhong

from __future__ import annotations


# try fastapi streaming response
# https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json

app = FastAPI()


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
        yield f"data: {json.dumps({'data': i})}\n\n"


# Swagger UI is NOT a streaming client
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
