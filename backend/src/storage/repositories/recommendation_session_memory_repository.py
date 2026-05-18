from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session
from sqlmodel import col
from sqlmodel import delete
from sqlmodel import select

from storage.identifiers import normalize_identifier_to_uuid
from storage.models.recommendation_session_memory import RecommendationSessionMemoryRecord


class RecommendationSessionMemoryRepository:
    """Repository for recommendation session memory records."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_by_session(
        self,
        user_id: UUID | str,
        session_id: UUID | str,
    ) -> list[RecommendationSessionMemoryRecord]:
        """Load session memory rows ordered by chat history number."""
        resolved_user_id = _coerce_uuid(user_id, field_name="user_id")
        resolved_session_id = _coerce_uuid(session_id, field_name="session_id")

        statement = (
            select(RecommendationSessionMemoryRecord)
            .where(
                col(RecommendationSessionMemoryRecord.user_id) == resolved_user_id,
                col(RecommendationSessionMemoryRecord.session_id) == resolved_session_id,
            )
            .order_by(col(RecommendationSessionMemoryRecord.chat_history_number))
        )
        return list(self.session.exec(statement).all())

    def upsert_many(self, rows: Sequence[RecommendationSessionMemoryRecord]) -> None:
        """Insert or update memory rows by composite primary key."""
        if not rows:
            return

        payloads = [row.model_dump(exclude_none=True) for row in rows]
        statement = insert(RecommendationSessionMemoryRecord).values(payloads)
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
        user_id: UUID | str,
        session_id: UUID | str,
    ) -> None:
        """Delete all rows for a user/session pair."""
        resolved_user_id = _coerce_uuid(user_id, field_name="user_id")
        resolved_session_id = _coerce_uuid(session_id, field_name="session_id")

        statement = delete(RecommendationSessionMemoryRecord).where(
            col(RecommendationSessionMemoryRecord.user_id) == resolved_user_id,
            col(RecommendationSessionMemoryRecord.session_id) == resolved_session_id,
        )
        self.session.exec(statement)


def _coerce_uuid(value: UUID | str, *, field_name: str) -> UUID:
    return normalize_identifier_to_uuid(value, field_name=field_name)
