from dataclasses import dataclass
from typing import Any, Literal, Optional

from langchain_core.language_models.chat_models import BaseChatModel

LLMProvider = Literal["chatgpt", "ollama"]

@dataclass()
class LLMConfig:
    """
    Unified chat model config.

    Defaults to Llama 3.1 via Ollama.

    Required deps (install only what you use):
      - chatgpt → langchain-openai
      - ollama  → langchain-ollama
    """

    provider: LLMProvider = "ollama"
    model: str = "llama3.1"

    # Common
    temperature: float = 0.2
    max_tokens: Optional[int] = None
    timeout_s: float = 60.0
    max_retries: int = 2

    # Provider specific
    api_key: Optional[str] = None
    base_url: Optional[str] = None  # OpenAI-compatible or Ollama host

    extra: Optional[dict[str, Any]] = None

    def get_common(self) -> dict[str, Any]:
        return {
            "temperature": self.temperature,
            "timeout": self.timeout_s,
            "max_retries": self.max_retries,
            **(self.extra or {}),
        }
