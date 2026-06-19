from __future__ import annotations

from datetime import UTC
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import text
from sqlmodel import Field
from sqlmodel import SQLModel


class SurveyQuestion(SQLModel, table=True):
    """Survey question record with numerical id and question text."""

    __tablename__ = "survey_questions"

    id: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            primary_key=True,
            nullable=False,
            server_default=text("GENERATED ALWAYS AS IDENTITY"),
        ),
    )
    question_text: str

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
    )
