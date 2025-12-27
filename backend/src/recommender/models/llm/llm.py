from langchain_core.language_models.chat_models import BaseChatModel
from typing import Any, Literal, Optional

from llm_config import LLMConfig

def create_chat_gpt_chat_model(cfg: LLMConfig) -> BaseChatModel:
    from langchain_openai import ChatOpenAI

    params: dict[str, Any] = {
        "model": cfg.model,
        **cfg.get_common(),
    }
    if cfg.max_tokens is not None:
        params["max_tokens"] = cfg.max_tokens
    if cfg.api_key is not None:
        params["api_key"] = cfg.api_key
    if cfg.base_url is not None:
        params["base_url"] = cfg.base_url

    return ChatOpenAI(**params)

def create_llama_chat_model(cfg: LLMConfig) -> BaseChatModel:
    from langchain_ollama import ChatOllama

    params: dict[str, Any] = {
        "model": cfg.model,
        **cfg.get_common(),
    }
    if cfg.base_url is not None:
        params["base_url"] = cfg.base_url

    if cfg.max_tokens is not None:
        params["num_predict"] = cfg.max_tokens

    return ChatOllama(**params)

def create_llm_chat_model(cfg: LLMConfig) -> BaseChatModel:
    if cfg.provider == "chatgpt":
        return create_chat_gpt_chat_model(cfg)
    if cfg.provider == "ollama":
        return create_llama_chat_model(cfg)
    raise ValueError(f"Unsupported LLM provider: {cfg.provider}")