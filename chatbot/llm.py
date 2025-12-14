"""Helpers for configuring ZhipuAI chat and embedding models."""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.embeddings import ZhipuAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatZhipuAI
from langchain_deepseek import ChatDeepSeek
from langchain_core.language_models import BaseChatModel


def get_api_key() -> str:
    """Load the ZhipuAI API key from the project's `.env` file."""
    env_path = Path(".env")
    # Load environment variables once at import time; keeps secrets out of code.
    load_dotenv(dotenv_path=env_path)
    api_key = os.getenv("BIGMODEL_API_KEY")
    assert api_key is not None
    return api_key


def get_zhipu_chat_model() -> ChatZhipuAI:
    """Create a ChatOpenAI-compatible client pointed at Zhipu's API."""
    # Use the OpenAI-compatible wrapper so we can talk to Zhipu with the same interface.
    # Commented block shows the native client if you prefer the direct integration.
    return ChatZhipuAI(
        model="glm-4.6",
        temperature=0.5,
        api_key=get_api_key(),
    )

    # return ChatOpenAI(
    #     model="glm-4.6",
    #     temperature=0.5,
    #     api_key=get_api_key(),
    #     # Zhipu exposes an OpenAI-compatible endpoint; point the wrapper there.
    #     base_url="https://open.bigmodel.cn/api/paas/v4/",
    # )


def get_embedding_model() -> ZhipuAIEmbeddings:
    """Create a ZhipuAIEmbeddings client for semantic embedding generation."""
    return ZhipuAIEmbeddings(model="embedding-3", api_key=get_api_key())


# https://docs.langchain.com/oss/python/integrations/chat/deepseek
def get_deepseek_chat_model() -> ChatDeepSeek:
    return ChatDeepSeek(
        model="deepseek-chat",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key="sk-892c31b494064a2bb1aebbde125e7459",
    )


def get_chat_model() -> BaseChatModel:
    return get_deepseek_chat_model()
