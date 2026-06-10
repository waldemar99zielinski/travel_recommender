from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from storage.db.unit_of_work import StorageUnitOfWork
from storage.models.chat_record import ChatRecord
from storage.repositories.chat_repository import (
    ChatRepository,
)


class ChatStore:
    """Store facade for chat session memory."""

    def __init__(self, unit_of_work: StorageUnitOfWork) -> None:
        self.unit_of_work = unit_of_work

    def load_session(
        self,
        user_id: UUID | str,
        session_id: UUID | str,
    ) -> list[ChatRecord]:
        """Load persisted rows for one user/session pair."""
        with self.unit_of_work.read() as session:
            repository = ChatRepository(session)
            return repository.list_by_session(user_id=user_id, session_id=session_id)

    def upsert_many(self, rows: Sequence[ChatRecord]) -> None:
        """Insert or update many session memory rows."""
        with self.unit_of_work.write() as session:
            repository = ChatRepository(session)
            repository.upsert_many(rows)

    def delete_session(
        self,
        user_id: UUID | str,
        session_id: UUID | str,
    ) -> None:
        """Delete all rows for one user/session pair."""
        with self.unit_of_work.write() as session:
            repository = ChatRepository(session)
            repository.delete_by_session(user_id=user_id, session_id=session_id)
