from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field


class SessionRefDto(BaseModel):
    user_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)


class SessionCreateRequestDto(BaseModel):
    user_id: str | None = Field(default=None)


class SessionCreateResponseDto(BaseModel):
    session: SessionRefDto = Field(...)


class SessionStateResponseDto(BaseModel):
    session: SessionRefDto = Field(...)


class SessionDeleteResponseDto(BaseModel):
    session: SessionRefDto = Field(...)
