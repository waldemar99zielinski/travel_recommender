from __future__ import annotations

from datetime import datetime

from sqlmodel import Field
from sqlmodel import SQLModel


class RecommendationSessionMemoryTable(SQLModel, table=True):
    """SQLModel table for session memory storage."""

    user_id: str = Field(primary_key=True)
    session_id: str = Field(primary_key=True)

    chat_history_number: int = Field(primary_key=True)

    user_request: str = Field(default="")
    system_response: str = Field(default="")

    query: str = Field(default="")
    interest_preference: str = Field(default="{}")
    logistical_preference: str = Field(default="{}")

    updated_at: datetime = Field(default_factory=datetime.now)
