from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field

from recommender.graphs.recommendation_v0.models import RecommendationV0


class AgentOutput(BaseModel):
    """Structured output returned by the recommendation_v0 agent."""

    system_response: str = Field(
        ...,
        description="Natural language response to the user",
    )
    recommendations: list[RecommendationV0] = Field(
        default_factory=list,
        description="List of recommended regions with explanations",
    )
