from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel
from pydantic import Field

from recommender.graphs.recommendation_v2.filter_models import (
    RecommendationV2BudgetFilter,
    RecommendationV2RegionFilter,
    RecommendationV2SeasonalityFilter,
    RecommendationV2TravelDestinationFilter,
)
from recommender.models.session.session import Session
from storage.models.chat_record import ChatRecord


class RecommendationV2StatusEnum(str, Enum):
    """Execution status for the template recommendation_v2 graph."""

    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    ERROR = "error"


class RecommendationV2(BaseModel):
    """Forward-compatible recommendation payload for recommendation_v2."""

    region_id: str = Field(..., description="ID of the recommended region")
    region_name: str = Field(..., description="Name of the recommended region")

    def serialize(self) -> dict[str, object]:
        return {
            "region_id": self.region_id,
            "region_name": self.region_name,
        }


class RecommendationV2RegionResearch(BaseModel):
    """Researched content for one recommended region."""

    description: str = Field(
        ...,
        description="Tailored researched description for the recommended region",
    )
    image_urls: list[str] = Field(
        default_factory=list,
        description="Relevant travel image URLs for the recommended region",
    )

    def serialize(self) -> dict[str, object]:
        return {
            "description": self.description,
            "image_urls": self.image_urls,
        }


def serialize_recommendations(recommendations: list[RecommendationV2] | None) -> str:
    """Serialize recommendations into a compact prompt-friendly string."""

    if not recommendations:
        return "None"

    return "\n".join(
        f"- region_id={recommendation.region_id}; region_name={recommendation.region_name}"
        for recommendation in recommendations
    )


class RecommendationV2GraphState(BaseModel):
    """State carried through the template recommendation_v2 graph."""

    session: Session = Field(..., description="Conversation scope identifiers")
    user_request: str = Field(..., description="Raw user query input")
    synthesized_user_request: str | None = Field(
        None,
        description="Synthetically generated user request to be used for retrieval and recommendation",
    )
    synthesized_user_request_keywords: list[str] = Field(
        default_factory=list,
        description="Keywords extracted from the synthesized user request for direct string search",
    )
    previous_synthesized_user_request: str | None = Field(
        None,
        description="Synthetically generated user request from the previous turn, used to detect changes in user intent",
    )
    #TODO load this in the session load
    previously_extracted_travel_destination_filter: RecommendationV2TravelDestinationFilter | None = Field(
        None,
        description="Travel destination filter extracted from the previous turn, used to detect changes in user intent",
    )
    extracted_parent_region_filters: list[RecommendationV2RegionFilter] = Field(
        default_factory=list,
        description="Parent-region filters extracted from the current turn with include/exclude intent",
    )
    parent_region_filter_removed: bool = Field(
        False,
        description="Whether the current turn explicitly removes parent-region filters",
    )
    extracted_seasonality_filter: RecommendationV2SeasonalityFilter | None = Field(
        None,
        description="Seasonality filter extracted for the current turn",
    )
    seasonality_filter_removed: bool = Field(
        False,
        description="Whether the current turn explicitly removes seasonality filters",
    )
    extracted_budget_filter: RecommendationV2BudgetFilter | None = Field(
        None,
        description="Budget filter extracted for the current turn",
    )
    budget_filter_removed: bool = Field(
        False,
        description="Whether the current turn explicitly removes budget filters",
    )
    gathered_travel_destination_filter: RecommendationV2TravelDestinationFilter | None = Field(
        None,
        description="Composed travel destination filter assembled by gather_requirements_node, used downstream for response generation and persistence",
    )
    system_response: str | None = Field(
        None,
        description="Final response message for the user",
    )
    recommendations: list[RecommendationV2] | None = Field(
        None,
        description="Generated recommendation candidates returned from future v2 nodes",
    )
    final_recommendations: list[RecommendationV2] | None = Field(
        None,
        description="Final recommendations remaining after the filter is applied",
    )
    travel_destinations_evaluations: dict[str, RecommendationV2RegionResearch] = Field(
        default_factory=dict,
        description="Researched region content keyed by recommended region_id",
    )
    history: list[ChatRecord] | None = Field(
        None,
        description="Persisted session turns loaded from storage",
    )
    request_routing_decision: Literal[
        "out_of_system_scope",
        "new_recommendation_run",
        "need_more_information_from_user",
    ] | None = Field(
        None,
        description="Routing decision produced for the current user turn",
    )
    request_routing_reason: str | None = Field(
        None,
        description="Short explanation for the routing decision",
    )

def serialize_chat_history(history: list[ChatRecord] | None) -> str:
    """Serialize chat history into a compact string format for LLM input."""
    if not history:
        return "None"

    parts: list[str] = []
    for row in history:
        parts.append(
            "User: "
            f"{row.user_request.strip() or 'None'}\n"
            "Assistant: "
            f"{row.system_response.strip() or 'None'}\n"
        )

    return "\n\n".join(parts)

__all__ = [
    "RecommendationV2",
    "RecommendationV2GraphState",
    "RecommendationV2RegionResearch",
    "RecommendationV2StatusEnum",
    "serialize_recommendations",
    "serialize_chat_history",
]
