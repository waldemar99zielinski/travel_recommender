from __future__ import annotations

from typing import Protocol


class TextEmbeddingModelProtocol(Protocol):
    """Contract for text-to-vector embedding providers."""

    def get_dimentions(self) -> int:
        """Return embedding vector dimension for this provider."""
        ...

    def embed_query(self, text: str) -> list[float]:
        """Return a single embedding vector for one query string."""
        ...
