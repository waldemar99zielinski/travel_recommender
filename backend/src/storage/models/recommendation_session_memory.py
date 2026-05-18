from __future__ import annotations

from datetime import UTC
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlmodel import Field
from sqlmodel import SQLModel


class RecommendationSessionMemoryRecord(SQLModel, table=True):
    """PostgreSQL record for persisted recommendation session memory."""

    __tablename__ = "recommendation_session_memory"  # type: ignore[assignment]

    user_id: UUID | None = Field(
        default=None,
        sa_column=Column(
            PostgreSQLUUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=text("uuidv7()"),
        ),
    )
    session_id: UUID | None = Field(
        default=None,
        sa_column=Column(
            PostgreSQLUUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=text("uuidv7()"),
        ),
    )
    chat_history_number: int = Field(primary_key=True)

    user_request: str = Field(default="")
    system_response: str = Field(default="")
    system_messages: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False, server_default=text("'[]'::jsonb")),
    )
    query: str = Field(default="")
    recommendations: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False, server_default=text("'[]'::jsonb")),
    )
    interest_preference: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default=text("'{}'::jsonb")),
    )
    logistical_preference: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default=text("'{}'::jsonb")),
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
    )
