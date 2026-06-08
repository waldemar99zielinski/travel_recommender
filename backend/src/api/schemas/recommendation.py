from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from pydantic import BaseModel
from pydantic import Field

from api.schemas.chat import ChatMessageDto
from api.schemas.session import SessionRefDto


class RecommendationRequestDto(BaseModel):
    session: SessionRefDto = Field(...)
    message: str = Field(..., min_length=1)
    included_regions_ids: list[str] = Field(default_factory=list)
    excluded_regions_ids: list[str] = Field(default_factory=list)

class RecommendationResponseDto(BaseModel):
    system_response: str = Field(default="")
    recommendations: list[dict[str, Any]] = Field(default_factory=list)
    travel_destinations_evaluations: list[dict[str, Any]] = Field(default_factory=list)
