from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from storage.models.recommendation_session_memory import RecommendationSessionMemoryRecord
from storage.models.storage_metadata import StorageMetadataRecord
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
        limit: int | None = None,
    ) -> list[ScoredTravelDestination]: ...

    def hybrid_search(
        self,
        query_embedding: Sequence[float],
        *,
        constraints: TravelSearchConstraints,
        limit: int | None = None,
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


class StorageMetadataRepositoryProtocol(Protocol):
    """Contract for storage metadata key-value persistence."""

    def list_all(self) -> list[StorageMetadataRecord]: ...

    def get(self, key: str) -> StorageMetadataRecord | None: ...

    def get_value(self, key: str) -> str | None: ...

    def upsert_many(self, rows: Sequence[StorageMetadataRecord]) -> None: ...

    def upsert(self, key: str, value: str) -> None: ...

    def delete(self, key: str) -> None: ...
