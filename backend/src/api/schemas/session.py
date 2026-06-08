from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from pydantic import Field

from api.schemas.chat import ChatRecordDto


class SessionRefDto(BaseModel):
    user_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    # TODO make an enum for versioning
    version: str = Field(default="v1", min_length=1)

class SessionCreateRequestDto(BaseModel):
    user_id: str | None = Field(default=None)

class SessionCreateResponseDto(BaseModel):
    session: SessionRefDto = Field(...)

class SessionGetRequestDto(BaseModel):
    user_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)

class SessionStateResponseDto(BaseModel):
    session: SessionRefDto = Field(...)
    chat_history: list[ChatRecordDto] = Field(default_factory=list)

class SessionDeleteResponseDto(BaseModel):
    session: SessionRefDto = Field(...)
