from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class OllamaTextEmbeddingModelConfiguration(BaseSettings):
    """Configuration for the Ollama text embedding provider."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_prefix="EMBEDDINGS_",
        extra="ignore",
    )

    model_name: str = Field(
        min_length=1,
        description="Ollama model identifier used for embedding generation.",
    )
    base_url: str = Field(
        min_length=1,
        description="Ollama host URL (for example http://localhost:11434).",
    )


def load_ollama_text_embedding_model_configuration(
    *,
    env_file: Path | str | None = None,
) -> OllamaTextEmbeddingModelConfiguration:
    """Load Ollama embedding settings from environment variables."""
    if env_file is None:
        return OllamaTextEmbeddingModelConfiguration()

    return OllamaTextEmbeddingModelConfiguration(_env_file=env_file)
