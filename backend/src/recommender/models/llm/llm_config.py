from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

LLMProvider = Literal["chatgpt", "ollama"]


class LLMConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[4] / ".env",
        env_prefix="LLM_",
        extra="ignore",
    )

    provider: LLMProvider = Field(default="ollama")
    model: str = Field(default="llama3.1")

    temperature: float = Field(default=0.2)
    max_tokens: Optional[int] = Field(default=None)
    timeout_s: float = Field(default=60.0)
    max_retries: int = Field(default=2)

    api_key: Optional[str] = Field(default=None)
    base_url: Optional[str] = Field(default=None)

    extra: Optional[dict[str, Any]] = Field(default=None)

    def get_common(self) -> dict[str, Any]:
        return {
            "temperature": self.temperature,
            "timeout": self.timeout_s,
            "max_retries": self.max_retries,
            **(self.extra or {}),
        }
