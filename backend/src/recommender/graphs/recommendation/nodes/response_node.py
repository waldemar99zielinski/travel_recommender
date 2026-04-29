from __future__ import annotations

from typing import Callable

from recommender.agents.response_generation.recommendation_response_generation_agent import (
    RecommendationResponseGenerationInput,
    RecommendationResponseGenerationAgent,
)
from recommender.graphs.recommendation.models import RecommendationGraphState
from recommender.graphs.recommendation.models import RecommendationStatusEnum


def create_response_node(
    response_generation_agent: RecommendationResponseGenerationAgent,
) -> Callable[[RecommendationGraphState], dict[str, object]]:
    """Create final response node for all graph exits."""

    def response_node(state: RecommendationGraphState) -> dict[str, object]:
        recommendations = state.recommendation or []
        generation_input = RecommendationResponseGenerationInput(
            user_input=state.user_input,
            status=state.status,
            interest_preferences=state.extracted_user_interests_preferences,
            logistical_preferences=state.extracted_user_logistical_preferences,
            recommendations=recommendations,
        )

        generation_result = response_generation_agent.invoke(
            generation_input,
        )

        return {
            "response": generation_result.message,
            "status": RecommendationStatusEnum.SUCCESS,
        }

    return response_node
