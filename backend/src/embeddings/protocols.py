from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol


class TextEmbeddingModelProtocol(Protocol):
    """Contract for text-to-vector embedding providers."""

    def embed_query(self, text: str) -> list[float]:
        """Return a single embedding vector for one query string."""
        ...

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        """Return embedding vectors for multiple text inputs."""
        ...
