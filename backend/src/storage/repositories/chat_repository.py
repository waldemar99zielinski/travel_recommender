from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session
from sqlmodel import col
from sqlmodel import delete
from sqlmodel import select

from storage.models.chat_record import ChatRecord


class ChatRepository:
    """Repository for chat session memory records."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_by_session(
        self,
        user_id: UUID,
        session_id: UUID,
    ) -> list[ChatRecord]:
        """Load session memory rows ordered by chat history number."""

        statement = (
            select(ChatRecord)
            .where(
                col(ChatRecord.user_id) == user_id,
                col(ChatRecord.session_id) == session_id,
            )
            .order_by(col(ChatRecord.chat_history_number))
        )
        return list(self.session.exec(statement).all())

    def upsert_many(self, rows: Sequence[ChatRecord]) -> None:
        """Insert or update memory rows by composite primary key."""
        if not rows:
            return

        payloads = [row.model_dump(exclude_none=True) for row in rows]
        statement = insert(ChatRecord).values(payloads)
        updatable_columns = {
            field_name: getattr(statement.excluded, field_name)
            for field_name in payloads[0]
            if field_name not in {"user_id", "session_id", "chat_history_number"}
        }

        upsert_statement = statement.on_conflict_do_update(
            index_elements=["user_id", "session_id", "chat_history_number"],
            set_=updatable_columns,
        )
        self.session.exec(upsert_statement)

    def delete_by_session(
        self,
        user_id: UUID,
        session_id: UUID,
    ) -> None:
        """Delete all rows for a user/session pair."""

        statement = delete(ChatRecord).where(
            col(ChatRecord.user_id) == user_id,
            col(ChatRecord.session_id) == session_id,
        )
        self.session.exec(statement)
