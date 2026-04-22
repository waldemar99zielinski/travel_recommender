from __future__ import annotations

from collections.abc import Sequence

from embeddings.protocols import TextEmbeddingModelProtocol
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
        embedding_model: TextEmbeddingModelProtocol,
    ) -> None:
        if embedding_model is None:
            raise ValueError("embedding_model is required")

        self.unit_of_work = unit_of_work
        self.embedding_model = embedding_model
        self.embedding_dimension = embedding_model.get_dimentions()

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
        query: str,
        limit: int | None = None,
    ) -> list[ScoredTravelDestination]:
        """Run nearest-neighbor semantic search over embedding vectors."""
        query_embedding = self._embed_query(query)
        with self.unit_of_work.read() as session:
            repository = TravelDestinationRepository(
                session,
                embedding_dimension=self.embedding_dimension,
            )
            return repository.semantic_search(query_embedding=query_embedding, limit=limit)

    def hybrid_search(
        self,
        query: str,
        *,
        constraints: TravelSearchConstraints,
        limit: int | None = None,
        semantic_weight: float = 0.85,
        logistics_weight: float = 0.15,
    ) -> list[ScoredTravelDestination]:
        """Run blended semantic + logistics search."""
        query_embedding = self._embed_query(query)
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
        query: str,
        limit: int | None = None,
    ) -> list[ScoredTravelDestination]:
        """Backward-compatible alias for semantic vector search."""
        return self.semantic_search(query=query, limit=limit)

    def _embed_query(self, query: str) -> list[float]:
        if not query.strip():
            raise ValueError("query must not be empty")

        query_embedding = self.embedding_model.embed_query(query)
        if len(query_embedding) != self.embedding_dimension:
            raise ValueError(
                "Query embedding dimension mismatch: "
                f"expected {self.embedding_dimension}, got {len(query_embedding)}"
            )

        return query_embedding
