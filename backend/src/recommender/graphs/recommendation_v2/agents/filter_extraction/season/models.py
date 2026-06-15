from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field

from recommender.graphs.recommendation_v2.filter_models import MonthCode
from recommender.graphs.recommendation_v2.filter_models import SeasonCode


class RecommendationV2SeasonFilterExtractionInput(BaseModel):
    """Input payload for recommendation_v2 season-filter extraction."""

    current_user_request: str = Field(
        ...,
        description="Raw user request from the current chat turn",
    )
    previous_season: SeasonCode | None = Field(
        None,
        description="Previously extracted season filter for this session",
    )
    previous_months: list[MonthCode] = Field(
        default_factory=list,
        description="Previously extracted month filters for this session",
    )


class RecommendationV2SeasonFilterExtractionResult(BaseModel):
    """Structured season filters extracted for recommendation_v2."""

    filter_removed: bool = Field(
        False,
        description="Whether the user explicitly requested removal of the seasonality filter category.",
    )

    season: SeasonCode | None = Field(
        None,
        description="Updated season filter after applying the current user request",
    )
    months: list[MonthCode] = Field(
        default_factory=list,
        description="Updated month filters after applying the current user request",
    )
