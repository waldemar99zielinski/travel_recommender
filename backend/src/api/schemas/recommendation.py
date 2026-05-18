from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel
from pydantic import Field

from api.schemas.chat_message import ChatMessageDto

if TYPE_CHECKING:
    from storage.stores.search_models import ScoredTravelDestination


class RecommendationRequestDto(BaseModel):
    user_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)


class RecommendationItemDto(BaseModel):
    id: str = Field(...)
    title: str = Field(...)
    score: float = Field(...)
    description: str = Field(...)

    @classmethod
    def from_recommendation(cls, recommendation: ScoredTravelDestination) -> RecommendationItemDto:
        score = recommendation.ranking_score
        destination = recommendation.destination

        return cls(
            id=destination.id,
            title=destination.region,
            score=float(score),
            description=destination.description,
        )


class RecommendationResponseDto(BaseModel):
    messages: list[ChatMessageDto] = Field(default_factory=list)
    recommendations: list[RecommendationItemDto] = Field(default_factory=list)
