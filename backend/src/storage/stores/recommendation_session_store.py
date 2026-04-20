from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from storage.db.unit_of_work import StorageUnitOfWork
from storage.models.recommendation_session_memory import RecommendationSessionMemoryRecord
from storage.repositories.recommendation_session_memory_repository import (
    RecommendationSessionMemoryRepository,
)


class RecommendationSessionStore:
    """Store facade for recommendation session memory."""

    def __init__(self, unit_of_work: StorageUnitOfWork) -> None:
        self.unit_of_work = unit_of_work

    def load_session(
        self,
        user_id: UUID | str,
        session_id: UUID | str,
    ) -> list[RecommendationSessionMemoryRecord]:
        """Load persisted rows for one user/session pair."""
        with self.unit_of_work.read() as session:
            repository = RecommendationSessionMemoryRepository(session)
            return repository.list_by_session(user_id=user_id, session_id=session_id)

    def upsert_many(self, rows: Sequence[RecommendationSessionMemoryRecord]) -> None:
        """Insert or update many session memory rows."""
        with self.unit_of_work.write() as session:
            repository = RecommendationSessionMemoryRepository(session)
            repository.upsert_many(rows)

    def delete_session(
        self,
        user_id: UUID | str,
        session_id: UUID | str,
    ) -> None:
        """Delete all rows for one user/session pair."""
        with self.unit_of_work.write() as session:
            repository = RecommendationSessionMemoryRepository(session)
            repository.delete_by_session(user_id=user_id, session_id=session_id)
