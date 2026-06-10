from __future__ import annotations

from collections.abc import Sequence

from embeddings.protocols import TextEmbeddingModelProtocol
from storage.db.unit_of_work import StorageUnitOfWork
from storage.models.travel_destination import TravelDestinationRecord
from storage.repositories.travel_destination_repository import TravelDestinationRepository
from storage.stores.query_models import QueriedTravelDestination
from storage.stores.query_models import TravelDestinationQuery
from storage.stores.search_models import TravelCostStatistics
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

    def cost_per_week_statistics(self) -> TravelCostStatistics:
        """Return percentile statistics for destination weekly costs."""
        with self.unit_of_work.read() as session:
            repository = TravelDestinationRepository(
                session,
                embedding_dimension=self.embedding_dimension,
            )
            return repository.cost_per_week_statistics()

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

    def query(self, request: TravelDestinationQuery) -> list[QueriedTravelDestination]:
        """Run structured destination queries suitable for tool-calling interfaces."""
        query_embedding = None
        if request.semantic_query is not None:
            query_embedding = self._embed_query(request.semantic_query)

        with self.unit_of_work.read() as session:
            repository = TravelDestinationRepository(
                session,
                embedding_dimension=self.embedding_dimension,
            )
            return repository.query(request=request, query_embedding=query_embedding)

    def find(self, request: TravelDestinationQuery) -> list[TravelDestinationRecord]:
        """Return plain destination records matched by generic structured filters and sort."""
        with self.unit_of_work.read() as session:
            repository = TravelDestinationRepository(
                session,
                embedding_dimension=self.embedding_dimension,
            )
            return repository.find(request=request)

    def semantic_search(
        self,
        query: str,
        limit: int | None = None,
        destination_ids: Sequence[str] | None = None,
    ) -> list[ScoredTravelDestination]:
        """Run nearest-neighbor semantic search over embedding vectors."""
        query_embedding = self._embed_query(query)
        with self.unit_of_work.read() as session:
            repository = TravelDestinationRepository(
                session,
                embedding_dimension=self.embedding_dimension,
            )
            return repository.semantic_search(
                query_embedding=query_embedding,
                limit=limit,
                destination_ids=destination_ids,
            )

    def hybrid_search(
        self,
        query: str,
        *,
        constraints: TravelSearchConstraints,
        limit: int | None = None,
        semantic_weight: float = 0.85,
        logistics_weight: float = 0.15,
        destination_ids: Sequence[str] | None = None,
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
                destination_ids=destination_ids,
            )

    def exact_text_search(
        self,
        query: str,
        limit: int | None = None,
    ) -> list[ScoredTravelDestination]:
        """Run exact and full-text search over region and description fields."""
        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("query must not be empty")

        with self.unit_of_work.read() as session:
            repository = TravelDestinationRepository(
                session,
                embedding_dimension=self.embedding_dimension,
            )
            return repository.exact_text_search(normalized_query, limit=limit)

    def keyword_boosted_search(
        self,
        semantic_query: str,
        keywords: list[str],
        *,
        keyword_boost: float = 0.3,
        limit: int | None = None,
    ) -> list[ScoredTravelDestination]:
        """Run semantic search and boost results that match concrete keywords.

        Finds destinations by semantic similarity, then applies a ranking-score
        boost to any destination whose region/description also matches the given
        keywords. If no keywords are provided, falls through to pure semantic search.
        """
        semantic_results = self.semantic_search(semantic_query)

        if not keywords:
            return semantic_results

        keyword_query = " ".join(keywords).strip()
        if not keyword_query:
            return semantic_results

        keyword_results = self.exact_text_search(keyword_query)
        keyword_destination_ids: set[str] = {
            result.destination.id for result in keyword_results
        }
        if not keyword_destination_ids:
            return semantic_results

        boosted: list[ScoredTravelDestination] = []
        for result in semantic_results:
            if result.destination.id in keyword_destination_ids:
                boosted_ranking = result.ranking_score + keyword_boost
                boosted.append(
                    ScoredTravelDestination(
                        destination=result.destination,
                        embedding_distance=result.embedding_distance,
                        semantic_score=result.semantic_score,
                        logistics_score=result.logistics_score,
                        ranking_score=boosted_ranking,
                    )
                )
            else:
                boosted.append(result)

        boosted.sort(key=lambda x: x.ranking_score, reverse=True)
        return boosted

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
