from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field

from api.schemas.chat_message import ChatMessageDto
from api.schemas.recommendation import RecommendationItemDto


class SessionRefDto(BaseModel):
    user_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)


class SessionCreateRequestDto(BaseModel):
    user_id: str | None = Field(default=None)


class SessionCreateResponseDto(BaseModel):
    session: SessionRefDto = Field(...)


class SessionStateResponseDto(BaseModel):
    session: SessionRefDto = Field(...)
    history: list["SessionHistoryTurnDto"] = Field(default_factory=list)
    last_recommendation_result: list[RecommendationItemDto] = Field(default_factory=list)


class SessionHistoryTurnDto(BaseModel):
    chat_history_number: int = Field(..., ge=0)
    user_request: str = Field(...)
    system_messages: list[ChatMessageDto] = Field(default_factory=list)


class SessionDeleteResponseDto(BaseModel):
    session: SessionRefDto = Field(...)
