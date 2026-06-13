from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field

from recommender.graphs.recommendation_v1.models import RecommendationV1

class AgentOutput(BaseModel):
    system_response: str = Field(
        ...,
        description="Natural language response to the user",
    )

    recommendations: list[RecommendationV1] = Field(
        default_factory=list,
        description="List of recommended regions with explanations",
    )

