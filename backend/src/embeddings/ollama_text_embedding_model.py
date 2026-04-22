from __future__ import annotations

from collections.abc import Sequence

from langchain_core.embeddings import Embeddings
from langchain_ollama import OllamaEmbeddings

from embeddings.configuration import OllamaTextEmbeddingModelConfiguration
from embeddings.protocols import TextEmbeddingModelProtocol
from utils.logger import LoggerManager

DIMENSION_PROBE_TEXT = "dimension-probe"
HEALTH_CHECK_PROBE_TEXT = "health-check"

logger = LoggerManager.get_logger(__name__)


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

        using_custom_backend = backend is not None
        logger.info(
            "Initializing OllamaTextEmbeddingModel: model=%s base_url=%s custom_backend=%s",
            self.model_name,
            self.configuration.base_url,
            using_custom_backend,
        )

        if backend is not None:
            self.backend = backend
            logger.verbose("Using injected embedding backend implementation")
        else:
            backend_parameters: dict[str, str] = {
                "model": model_name,
                "base_url": configuration.base_url,
            }

            self.backend = OllamaEmbeddings(**backend_parameters)
            logger.verbose("Created OllamaEmbeddings backend from runtime configuration")

        if not self.check_health():
            raise RuntimeError(
                "OllamaTextEmbeddingModel health check failed during initialization. "
                "Verify EMBEDDINGS_MODEL_NAME, EMBEDDINGS_BASE_URL, and Ollama availability."
            )

        logger.info(
            "OllamaTextEmbeddingModel health check passed: model=%s dimensions=%s",
            self.model_name,
            self.get_dimentions(),
        )

    def get_dimentions(self) -> int:
        """Return stable embedding vector dimension for the configured model."""
        if self._dimension is None:
            logger.verbose("Resolving embedding dimensions using probe text")
            probe_embedding = self.backend.embed_query(DIMENSION_PROBE_TEXT)
            if not probe_embedding:
                logger.verbose("Embedding backend returned empty probe vector")
                raise RuntimeError("Embedding backend returned an empty probe vector")
            self._dimension = len(probe_embedding)
            logger.verbose("Resolved embedding dimensions: %s", self._dimension)
        logger.verbose("Using cached embedding dimensions: %s", self._dimension)
        return self._dimension

    def check_health(self) -> bool:
        """Return whether Ollama embedding calls succeed with consistent dimensions."""
        logger.verbose("Running embedding model health check")
        try:
            embedding = self.embed_query(HEALTH_CHECK_PROBE_TEXT)
        except Exception as error:
            logger.verbose("Embedding health check failed: %s", error)
            return False

        is_healthy = len(embedding) == self.get_dimentions()
        logger.verbose("Embedding health check result: healthy=%s", is_healthy)
        return is_healthy

    def embed_query(self, text: str) -> list[float]:
        """Return embedding vector for one query string."""
        normalized = text.strip()
        if not normalized:
            logger.verbose("Rejected empty query text for embedding")
            raise ValueError("text must not be empty")

        logger.verbose("Generating embedding for query text length=%s", len(normalized))
        embedding = self.backend.embed_query(normalized)
        normalized_embedding = [float(value) for value in embedding]
        self._validate_embedding_dimension(normalized_embedding)
        logger.verbose("Generated embedding vector with dimensions=%s", len(normalized_embedding))
        return normalized_embedding

    def _validate_embedding_dimension(self, embedding: Sequence[float]) -> None:
        embedding_dimension = len(embedding)
        if embedding_dimension <= 0:
            logger.verbose("Embedding backend returned empty vector during validation")
            raise RuntimeError("Embedding backend returned an empty vector")

        if self._dimension is None:
            self._dimension = embedding_dimension
            logger.verbose("Initialized cached embedding dimensions=%s", self._dimension)
            return

        if embedding_dimension != self._dimension:
            logger.verbose(
                "Detected inconsistent embedding dimensions expected=%s got=%s",
                self._dimension,
                embedding_dimension,
            )
            raise RuntimeError(
                "Embedding backend returned inconsistent dimensions: "
                f"expected {self._dimension}, got {embedding_dimension}"
            )

        logger.verbose("Validated embedding dimensions=%s", embedding_dimension)
