from __future__ import annotations

from pathlib import Path

from embeddings.configuration import TextEmbeddingModelConfiguration
from embeddings.configuration import load_text_embedding_model_configuration
from embeddings.openai_text_embedding_model import OpenAITextEmbeddingModel
from embeddings.ollama_text_embedding_model import OllamaTextEmbeddingModel
from embeddings.protocols import TextEmbeddingModelProtocol


def create_text_embedding_model(
    configuration: TextEmbeddingModelConfiguration,
) -> TextEmbeddingModelProtocol:
    """Create the configured embedding model implementation."""
    if configuration.provider == "ollama":
        return OllamaTextEmbeddingModel(configuration)
    if configuration.provider == "openai":
        return OpenAITextEmbeddingModel(configuration)

    raise ValueError(f"Unsupported embeddings provider: {configuration.provider}")


def load_text_embedding_model(
    *,
    env_file: Path | str | None = None,
) -> TextEmbeddingModelProtocol:
    """Load embedding configuration and create the matching embedding model."""
    configuration = load_text_embedding_model_configuration(env_file=env_file)
    return create_text_embedding_model(configuration)
