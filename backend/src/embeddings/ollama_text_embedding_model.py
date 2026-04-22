from __future__ import annotations

from collections.abc import Sequence

from langchain_core.embeddings import Embeddings
from langchain_ollama import OllamaEmbeddings

from embeddings.configuration import OllamaTextEmbeddingModelConfiguration
from embeddings.protocols import TextEmbeddingModelProtocol

DIMENSION_PROBE_TEXT = "dimension-probe"


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
        self._dimension: int | None = None

        if backend is not None:
            self.backend = backend
            return

        backend_parameters: dict[str, str] = {
            "model": model_name,
            "base_url": configuration.base_url,
        }

        self.backend = OllamaEmbeddings(**backend_parameters)

    def get_dimentions(self) -> int:
        """Return stable embedding vector dimension for the configured model."""
        if self._dimension is None:
            probe_embedding = self.backend.embed_query(DIMENSION_PROBE_TEXT)
            if not probe_embedding:
                raise RuntimeError("Embedding backend returned an empty probe vector")
            self._dimension = len(probe_embedding)
        return self._dimension

    def embed_query(self, text: str) -> list[float]:
        """Return embedding vector for one query string."""
        normalized = text.strip()
        if not normalized:
            raise ValueError("text must not be empty")

        embedding = self.backend.embed_query(normalized)
        normalized_embedding = [float(value) for value in embedding]
        self._validate_embedding_dimension(normalized_embedding)
        return normalized_embedding

    def _validate_embedding_dimension(self, embedding: Sequence[float]) -> None:
        embedding_dimension = len(embedding)
        if embedding_dimension <= 0:
            raise RuntimeError("Embedding backend returned an empty vector")

        if self._dimension is None:
            self._dimension = embedding_dimension
            return

        if embedding_dimension != self._dimension:
            raise RuntimeError(
                "Embedding backend returned inconsistent dimensions: "
                f"expected {self._dimension}, got {embedding_dimension}"
            )
