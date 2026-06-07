from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field

from recommender.graphs.recommendation_v2.filter_models import RecommendationV2RegionFilter


class RecommendationV2RegionsFilterExtractionInput(BaseModel):
    """Input payload for recommendation_v2 region-filter extraction from the current turn."""

    current_user_request: str = Field(
        ...,
        description="Raw user request from the current chat turn",
    )


class RecommendationV2RegionsFilterExtractionResult(BaseModel):
    """Structured region filters extracted for recommendation_v2."""

    regions: list[RecommendationV2RegionFilter] | None = Field(
        None,
        description="Parent-region or direct-region filters mapped from the current user request only",
    )
