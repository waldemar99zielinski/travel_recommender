from __future__ import annotations

from collections.abc import Sequence

from storage.configuration import DEFAULT_EMBEDDING_DIMENSION
from storage.db.unit_of_work import StorageUnitOfWork
from storage.models.travel_destination import TravelDestinationRecord
from storage.repositories.travel_destination_repository import TravelDestinationRepository
from storage.stores.search_models import ScoredTravelDestination
from storage.stores.search_models import TravelSearchConstraints


class TravelDestinationStore:
    """Store facade for travel destinations in PostgreSQL + pgvector."""

    def __init__(
        self,
        unit_of_work: StorageUnitOfWork,
        *,
        embedding_dimension: int = DEFAULT_EMBEDDING_DIMENSION,
    ) -> None:
        self.unit_of_work = unit_of_work
        self.embedding_dimension = embedding_dimension

    def size(self) -> int:
        """Return number of persisted travel destinations."""
        with self.unit_of_work.read() as session:
            repository = TravelDestinationRepository(
                session,
                embedding_dimension=self.embedding_dimension,
            )
            return repository.count()

    def all(self) -> list[TravelDestinationRecord]:
        """Return all persisted travel destinations."""
        with self.unit_of_work.read() as session:
            repository = TravelDestinationRepository(
                session,
                embedding_dimension=self.embedding_dimension,
            )
            return repository.list_all()

    def upsert_many(self, rows: Sequence[TravelDestinationRecord]) -> None:
        """Insert or update many travel destinations."""
        with self.unit_of_work.write() as session:
            repository = TravelDestinationRepository(
                session,
                embedding_dimension=self.embedding_dimension,
            )
            repository.upsert_many(rows)

    def list_by_ids(self, destination_ids: Sequence[str]) -> list[TravelDestinationRecord]:
        """Return travel destinations for selected IDs."""
        with self.unit_of_work.read() as session:
            repository = TravelDestinationRepository(
                session,
                embedding_dimension=self.embedding_dimension,
            )
            return repository.list_by_ids(destination_ids)

    def semantic_search(
        self,
        query_embedding: Sequence[float],
        limit: int = 5,
    ) -> list[ScoredTravelDestination]:
        """Run nearest-neighbor semantic search over embedding vectors."""
        with self.unit_of_work.read() as session:
            repository = TravelDestinationRepository(
                session,
                embedding_dimension=self.embedding_dimension,
            )
            return repository.semantic_search(query_embedding=query_embedding, limit=limit)

    def hybrid_search(
        self,
        query_embedding: Sequence[float],
        *,
        constraints: TravelSearchConstraints,
        limit: int = 5,
        semantic_weight: float = 0.85,
        logistics_weight: float = 0.15,
    ) -> list[ScoredTravelDestination]:
        """Run blended semantic + logistics search."""
        with self.unit_of_work.read() as session:
            repository = TravelDestinationRepository(
                session,
                embedding_dimension=self.embedding_dimension,
            )
            return repository.hybrid_search(
                query_embedding=query_embedding,
                constraints=constraints,
                limit=limit,
                semantic_weight=semantic_weight,
                logistics_weight=logistics_weight,
            )

    def vector_search(
        self,
        query_embedding: Sequence[float],
        limit: int = 5,
    ) -> list[ScoredTravelDestination]:
        """Backward-compatible alias for semantic vector search."""
        return self.semantic_search(query_embedding=query_embedding, limit=limit)
