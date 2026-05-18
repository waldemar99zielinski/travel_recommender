from __future__ import annotations

from enum import Enum

from pydantic import BaseModel
from pydantic import Field

from recommender.models.session.session import Session
from storage.models.recommendation_session_memory import RecommendationSessionMemoryRecord
from storage.stores.search_models import ScoredTravelDestination


class QuerySynthesisRoutingOutcome(str, Enum):
    """High-level response outcomes for recommendation_v3 routing."""

    OUTSIDE_OF_RECOMMENDER_SCOPE = "outside_of_recommender_scope"
    NOT_ENOUGH_INFORMATION_PROVIDED = "not_enough_information_provided"
    RUN_NEW_RECOMMENDATION = "run_new_recommendation"


class RecommendationV3GraphState(BaseModel):
    """State carried through the recommendation_v3 graph."""

    session: Session = Field(..., description="Conversation scope identifiers")
    user_input: str = Field(..., description="Raw user query input")
    synthesized_query: str | None = Field(None, description="Current synthesized query")
    previous_synthesized_query: str | None = Field(
        None,
        description="Most recent synthesized query from history",
    )
    routing_outcome: QuerySynthesisRoutingOutcome | None = Field(
        None,
        description="Routing outcome for the current turn",
    )
    routing_reason: str | None = Field(
        None,
        description="Short explanation for the chosen routing outcome",
    )
    recommendation: list[ScoredTravelDestination] | None = Field(
        None,
        description="Final recommendation list returned by the graph",
    )
    response: str | None = Field(None, description="Final response message")
    history: list[RecommendationSessionMemoryRecord] | None = Field(
        None,
        description="Persisted session turns loaded from storage",
    )
