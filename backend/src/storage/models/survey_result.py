from __future__ import annotations

from datetime import UTC
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field as PydanticField
from pydantic import model_serializer
from pydantic import model_validator
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.types import TypeDecorator
from sqlmodel import Field
from sqlmodel import SQLModel


class SurveyResultsData(BaseModel):
    """Mapping of question IDs to numeric scores with convenience accessors.

    Stored as a flat JSONB dict ``{"1": 5.0, "2": 3.5}`` in the database.
    """

    scores: dict[int, float] = PydanticField(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def _unwrap_flat_dict(cls, data: Any) -> Any:
        if isinstance(data, dict) and "scores" not in data:
            return {"scores": data}
        return data

    @model_serializer(mode="wrap")
    def _flatten_to_dict(self, handler) -> dict[str, float]:
        wrapped = handler(self)
        return dict(wrapped.get("scores", {}))

    def get(self, question_id: int, default: float | None = None) -> float | None:
        return self.scores.get(question_id, default)

    def set(self, question_id: int, score: float) -> None:
        self.scores[question_id] = score

    @property
    def average(self) -> float:
        if not self.scores:
            return 0.0
        return sum(self.scores.values()) / len(self.scores)

    @property
    def total(self) -> float:
        return sum(self.scores.values())

    def __getitem__(self, question_id: int) -> float:
        return self.scores[question_id]

    def __setitem__(self, question_id: int, score: float) -> None:
        self.scores[question_id] = score

    def __contains__(self, question_id: int) -> bool:
        return question_id in self.scores


class _SurveyResultsDB(TypeDecorator):
    """Transparently converts between JSONB dict and SurveyResultsData."""

    impl = JSONB
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Any) -> dict | None:
        if isinstance(value, SurveyResultsData):
            return value.model_dump(mode="json")
        return value

    def process_result_value(self, value: Any, dialect: Any) -> SurveyResultsData:
        if isinstance(value, dict):
            return SurveyResultsData.model_validate(value)
        return SurveyResultsData()


class SurveyResult(SQLModel, table=True):
    """Survey result record linking user and session to JSON results."""

    __tablename__ = "survey_results"

    id: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            primary_key=True,
            nullable=False,
            server_default=text("GENERATED ALWAYS AS IDENTITY"),
        ),
    )
    user_id: UUID = Field(
        sa_column=Column(
            PostgreSQLUUID(as_uuid=True),
            nullable=False,
        ),
    )
    session_id: UUID = Field(
        sa_column=Column(
            PostgreSQLUUID(as_uuid=True),
            nullable=False,
        ),
    )
    results: SurveyResultsData = Field(
        default_factory=SurveyResultsData,
        sa_column=Column(
            _SurveyResultsDB,
            nullable=False,
            server_default=text("'{}'::jsonb"),
        ),
    )
    comment: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
    )
