from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from storage.models.chat_record import ChatRecord
from storage.models.storage_metadata import StorageMetadataRecord
from storage.models.travel_destination import TravelDestinationRecord
from storage.stores.query_models import QueriedTravelDestination
from storage.stores.query_models import TravelDestinationQuery
from storage.stores.search_models import TravelCostStatistics
from storage.stores.search_models import ScoredTravelDestination
from storage.stores.search_models import TravelSearchConstraints


class TravelDestinationStoreProtocol(Protocol):
    """Contract for travel destination store operations."""

    def size(self) -> int: ...

    def all(self) -> list[TravelDestinationRecord]: ...

    def cost_per_week_statistics(self) -> TravelCostStatistics: ...

    def upsert_many(self, rows: Sequence[TravelDestinationRecord]) -> None: ...

    def list_by_ids(self, destination_ids: Sequence[str]) -> list[TravelDestinationRecord]: ...

    def query(self, request: TravelDestinationQuery) -> list[QueriedTravelDestination]: ...

    def find(self, request: TravelDestinationQuery) -> list[TravelDestinationRecord]: ...

    def semantic_search(
        self,
        query: str,
        limit: int | None = None,
        destination_ids: Sequence[str] | None = None,
    ) -> list[ScoredTravelDestination]: ...

    def vector_search(
        self,
        query: str,
        limit: int | None = None,
    ) -> list[ScoredTravelDestination]: ...

    def hybrid_search(
        self,
        query: str,
        *,
        constraints: TravelSearchConstraints,
        limit: int | None = None,
        semantic_weight: float = 0.85,
        logistics_weight: float = 0.15,
        destination_ids: Sequence[str] | None = None,
    ) -> list[ScoredTravelDestination]: ...

    def exact_text_search(
        self,
        query: str,
        limit: int | None = None,
    ) -> list[ScoredTravelDestination]: ...

    def keyword_boosted_search(
        self,
        semantic_query: str,
        keywords: list[str],
        *,
        keyword_boost: float = 0.3,
        limit: int | None = None,
    ) -> list[ScoredTravelDestination]: ...


class ChatStoreProtocol(Protocol):
    """Contract for chat session memory operations."""

    def load_session(
        self,
        user_id: UUID | str,
        session_id: UUID | str,
    ) -> list[ChatRecord]: ...

    def upsert_many(self, rows: Sequence[ChatRecord]) -> None: ...

    def delete_session(self, user_id: UUID | str, session_id: UUID | str) -> None: ...


class StorageMetadataStoreProtocol(Protocol):
    """Contract for storage metadata key-value store operations."""

    def list_all(self) -> list[StorageMetadataRecord]: ...

    def get(self, key: str) -> StorageMetadataRecord | None: ...

    def get_value(self, key: str) -> str | None: ...

    def upsert_many(self, rows: Sequence[StorageMetadataRecord]) -> None: ...

    def upsert(self, key: str, value: str) -> None: ...

    def delete(self, key: str) -> None: ...
