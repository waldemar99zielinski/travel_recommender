from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field

from recommender.graphs.recommendation_v2.filter_models import (
    RecommendationV2TravelDestinationFilter,
)
from recommender.graphs.recommendation_v2.models import RecommendationV2
from storage.models.chat_record import ChatRecord


class RecommendationV2RecommendationGeneratedResponseGenerationInput(BaseModel):
    """Input payload for recommendation_v2 responses when recommendations are available."""

    current_user_request: str = Field(
        ...,
        description="Raw user request from the current chat turn",
    )
    synthesized_user_request: str | None = Field(
        None,
        description="History-aware synthesized request when available",
    )
    travel_destination_filter: RecommendationV2TravelDestinationFilter | None = Field(
        None,
        description="Structured travel-destination filter extracted for this turn",
    )
    recommendations: list[RecommendationV2] | None = Field(
        None,
        description="Generated recommendation candidates for this turn",
    )
    chat_history: list[ChatRecord] | None = Field(
        None,
        description="Persisted chat history for the active session",
    )
