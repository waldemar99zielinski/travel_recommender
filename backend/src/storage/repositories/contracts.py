from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from storage.models.recommendation_session_memory import RecommendationSessionMemoryRecord
from storage.models.travel_destination import TravelDestinationRecord
from storage.stores.search_models import ScoredTravelDestination
from storage.stores.search_models import TravelSearchConstraints


class TravelDestinationRepositoryProtocol(Protocol):
    """Contract for travel destination persistence and retrieval."""

    def count(self) -> int: ...

    def list_all(self) -> list[TravelDestinationRecord]: ...

    def list_by_ids(self, destination_ids: Sequence[str]) -> list[TravelDestinationRecord]: ...

    def upsert_many(self, rows: Sequence[TravelDestinationRecord]) -> None: ...

    def semantic_search(
        self,
        query_embedding: Sequence[float],
        limit: int = 5,
    ) -> list[ScoredTravelDestination]: ...

    def hybrid_search(
        self,
        query_embedding: Sequence[float],
        *,
        constraints: TravelSearchConstraints,
        limit: int = 5,
        semantic_weight: float = 0.85,
        logistics_weight: float = 0.15,
    ) -> list[ScoredTravelDestination]: ...


class RecommendationSessionMemoryRepositoryProtocol(Protocol):
    """Contract for recommendation session memory persistence."""

    def list_by_session(
        self,
        user_id: UUID | str,
        session_id: UUID | str,
    ) -> list[RecommendationSessionMemoryRecord]: ...

    def upsert_many(self, rows: Sequence[RecommendationSessionMemoryRecord]) -> None: ...

    def delete_by_session(self, user_id: UUID | str, session_id: UUID | str) -> None: ...
