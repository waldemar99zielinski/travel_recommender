from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

EmbeddingProvider = Literal["ollama", "openai"]


class TextEmbeddingModelConfiguration(BaseSettings):
    """Configuration for the active text embedding provider."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_prefix="EMBEDDINGS_",
        extra="ignore",
    )

    provider: EmbeddingProvider = Field(
        default="ollama",
        description="Embedding provider used by the backend.",
    )
    model_name: str = Field(
        min_length=1,
        description="Provider model identifier used for embedding generation.",
    )
    base_url: str | None = Field(
        default=None,
        description="Optional provider base URL override.",
    )
    api_key: str | None = Field(
        default=None,
        description="Optional provider API key, required for OpenAI embeddings.",
    )


def load_text_embedding_model_configuration(
    *,
    env_file: Path | str | None = None,
) -> TextEmbeddingModelConfiguration:
    """Load embedding settings from environment variables."""
    if env_file is None:
        return TextEmbeddingModelConfiguration()

    return TextEmbeddingModelConfiguration(_env_file=env_file)
