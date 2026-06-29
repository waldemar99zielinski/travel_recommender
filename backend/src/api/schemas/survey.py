from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel
from pydantic import Field


class SurveyQuestionDto(BaseModel):
    id: int
    question_text: str


class SurveyResultCreateRequestDto(BaseModel):
    user_id: UUID
    session_id: UUID
    scores: dict[str, str | float | int] = Field(default_factory=dict)
    comment: str | None = None


class SurveyResultResponseDto(BaseModel):
    id: int
    user_id: UUID
    session_id: UUID
    scores: dict[str, str | float | int]
    comment: str | None
