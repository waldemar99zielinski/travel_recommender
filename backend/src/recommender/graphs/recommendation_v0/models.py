from __future__ import annotations

from enum import Enum

from pydantic import BaseModel
from pydantic import Field

from recommender.models.session.session import Session
from storage.models.chat_record import ChatRecord


class RecommendationV0StatusEnum(str, Enum):
    """Execution status for the single-node recommendation_v0 graph."""

    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    ERROR = "error"


class RecommendationV0GraphState(BaseModel):
    """State carried through recommendation_v0."""

    session: Session = Field(..., description="Conversation scope identifiers")
    user_request: str = Field(
        ...,
        description="Raw user query input",
    )
    included_regions_ids: list[str] = Field(
        default_factory=list,
        description="List of region IDs that the user has expressed interest in during the conversation",
    )
    excluded_regions_ids: list[str] = Field(
        default_factory=list,
        description="List of region IDs that the user has expressed disinterest in during the conversation",
    )
    system_response: str | None = Field(
        None,
        description="Final response message for the user",
    )
    recommendations: list[RecommendationV0] | None = Field(
        None,
        description="Ranked recommendations returned from the agent",
    )
    history: list[ChatRecord] | None = Field(
        None,
        description="Persisted session turns loaded from storage",
    )


class RecommendationV0(BaseModel):
    """Single recommended region and explanation."""

    region_id: str = Field(..., description="ID of the recommended region")
    explanation: str = Field(
        ...,
        description="Explanation for the recommendation",
    )

    def serialize(self) -> dict[str, object]:
        return {
            "region_id": self.region_id,
            "explanation": self.explanation,
        }


__all__ = ["RecommendationV0", "RecommendationV0GraphState", "RecommendationV0StatusEnum"]
