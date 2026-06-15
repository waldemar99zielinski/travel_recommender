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
        seasonality_months: Sequence[str] = (),
        limit: int | None = None,
    ) -> list[ScoredTravelDestination]:
        """Run recommendation retrieval: semantic search, IQR keyword boost, and seasonality re-ranking."""
        query_embedding = self._embed_query(semantic_query)
        normalized_months = _normalize_months(seasonality_months)

        with self.unit_of_work.read() as session:
            repository = TravelDestinationRepository(
                session,
                embedding_dimension=self.embedding_dimension,
            )
            semantic_results = repository.semantic_search(query_embedding=query_embedding)
            keyword_destination_ids = repository.keyword_matching_destination_ids(keywords)

        if not semantic_results:
            return []

        iqr = _interquartile_range([result.semantic_score for result in semantic_results])
        boosted_results = _apply_keyword_iqr_boost(
            semantic_results,
            keyword_destination_ids=keyword_destination_ids,
            boost=iqr,
        )
        reranked_results = _apply_seasonality_reranking(
            boosted_results,
            months=normalized_months,
        )
        reranked_results.sort(key=lambda result: result.ranking_score, reverse=True)

        if limit is not None:
            return reranked_results[:limit]
        return reranked_results

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


_VALID_MONTHS = {
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
}


def _apply_keyword_iqr_boost(
    results: list[ScoredTravelDestination],
    *,
    keyword_destination_ids: set[str],
    boost: float,
) -> list[ScoredTravelDestination]:
    boosted_results: list[ScoredTravelDestination] = []
    for result in results:
        keyword_indicator = 1.0 if result.destination.id in keyword_destination_ids else 0.0
        boosted_score = result.semantic_score + (keyword_indicator * boost)
        boosted_results.append(
            ScoredTravelDestination(
                destination=result.destination,
                embedding_distance=result.embedding_distance,
                semantic_score=result.semantic_score,
                logistics_score=result.logistics_score,
                ranking_score=boosted_score,
            )
        )
    return boosted_results


def _apply_seasonality_reranking(
    results: list[ScoredTravelDestination],
    *,
    months: Sequence[str],
) -> list[ScoredTravelDestination]:
    if not months:
        return results

    normalized_semantic_scores = _min_max_normalize(
        [result.ranking_score for result in results]
    )
    raw_seasonality_scores = [
        sum(float(getattr(result.destination, month)) for month in months)
        for result in results
    ]
    normalized_seasonality_scores = _min_max_normalize(raw_seasonality_scores)

    reranked_results: list[ScoredTravelDestination] = []
    for result, semantic_score, seasonality_score in zip(
        results,
        normalized_semantic_scores,
        normalized_seasonality_scores,
        strict=True,
    ):
        combined_score = (0.7 * semantic_score) + (0.3 * seasonality_score)
        reranked_results.append(
            ScoredTravelDestination(
                destination=result.destination,
                embedding_distance=result.embedding_distance,
                semantic_score=result.semantic_score,
                logistics_score=seasonality_score,
                ranking_score=combined_score,
            )
        )
    return reranked_results


def _interquartile_range(values: Sequence[float]) -> float:
    if not values:
        return 0.0

    sorted_values = sorted(float(value) for value in values)
    q1 = _percentile(sorted_values, 0.25)
    q3 = _percentile(sorted_values, 0.75)
    return q3 - q1


def _percentile(sorted_values: Sequence[float], percentile: float) -> float:
    if len(sorted_values) == 1:
        return sorted_values[0]

    index = percentile * (len(sorted_values) - 1)
    lower_index = int(index)
    upper_index = min(lower_index + 1, len(sorted_values) - 1)
    fraction = index - lower_index
    return sorted_values[lower_index] + (
        (sorted_values[upper_index] - sorted_values[lower_index]) * fraction
    )


def _min_max_normalize(values: Sequence[float]) -> list[float]:
    if not values:
        return []

    minimum = min(values)
    maximum = max(values)
    if maximum == minimum:
        return [1.0] * len(values)

    return [(value - minimum) / (maximum - minimum) for value in values]


def _normalize_months(months: Sequence[str]) -> tuple[str, ...]:
    normalized_months: list[str] = []
    for month in months:
        normalized_month = month.lower().strip()
        if normalized_month in _VALID_MONTHS and normalized_month not in normalized_months:
            normalized_months.append(normalized_month)
    return tuple(normalized_months)
