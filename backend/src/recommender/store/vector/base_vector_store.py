from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from recommender.models.data_flow.recommendation_output import Recommendation


class BaseVectorStore(ABC):
    """Abstract contract for vector stores used by the recommender."""

    @abstractmethod
    def build_from_csv(self, csv_file_path: str) -> None:
        """Build and persist vector index from CSV source data."""

    @abstractmethod
    def load(self) -> None:
        """Load persisted vector index into memory."""

    @abstractmethod
    def is_loaded(self) -> bool:
        """Return True when vector index is loaded in memory."""

    @abstractmethod
    def size(self) -> int:
        """Return number of indexed vectors."""

    @abstractmethod
    def search(self, query: str, k: int = 5) -> list[Recommendation]:
        """Run semantic search and return top-k recommendations."""

    @abstractmethod
    def search_all_ranked(self, query: str) -> list[Recommendation]:
        """Run semantic search against all indexed vectors."""
