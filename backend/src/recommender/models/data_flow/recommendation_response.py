from __future__ import annotations

from pydantic import BaseModel, Field

from recommender.models.data_flow.recommendation_output import Recommendation

class RecommendationResponse(BaseModel):
    """Final response payload shared across graph branches."""

    message: str = Field(
        ...,
        description="User-facing response message"
    )
    recommendations: list[Recommendation] = Field(
        default_factory=list,
        description="Ranked recommendations returned from vector search",
    )
