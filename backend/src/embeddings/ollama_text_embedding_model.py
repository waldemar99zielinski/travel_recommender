from __future__ import annotations

from collections.abc import Sequence

from langchain_core.embeddings import Embeddings
from langchain_ollama import OllamaEmbeddings

from embeddings.configuration import OllamaTextEmbeddingModelConfiguration
from embeddings.protocols import TextEmbeddingModelProtocol


class OllamaTextEmbeddingModel(TextEmbeddingModelProtocol):
    """Ollama-backed embedding provider used across storage and recommender."""

    def __init__(
        self,
        configuration: OllamaTextEmbeddingModelConfiguration,
        *,
        backend: Embeddings | None = None,
    ) -> None:
        if configuration is None:
            raise ValueError("configuration is required")

        model_name = configuration.model_name.strip()
        if not model_name:
            raise ValueError("model_name must not be empty")

        self.configuration = configuration
        self.model_name = model_name

        if backend is not None:
            self.backend = backend
            return

        backend_parameters: dict[str, str] = {"model": model_name}
        if configuration.base_url is not None:
            backend_parameters["base_url"] = configuration.base_url

        self.backend = OllamaEmbeddings(**backend_parameters)

    def embed_query(self, text: str) -> list[float]:
        """Return embedding vector for one query string."""
        normalized = text.strip()
        if not normalized:
            raise ValueError("text must not be empty")

        embedding = self.backend.embed_query(normalized)
        return [float(value) for value in embedding]

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        """Return embedding vectors for multiple text strings."""
        normalized_texts = [text.strip() for text in texts if text.strip()]
        if not normalized_texts:
            return []

        embeddings = self.backend.embed_documents(normalized_texts)
        return [[float(value) for value in vector] for vector in embeddings]
