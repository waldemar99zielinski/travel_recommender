from __future__ import annotations

from typing import Callable

from recommender.agents.response_generation.recommendation_v3_response_generation_agent import (
    RecommendationV3ResponseGenerationAgent,
)
from recommender.agents.response_generation.recommendation_v3_response_generation_agent import (
    RecommendationV3ResponseGenerationInput,
)
from recommender.graphs.recommendation_v3.models import RecommendationV3GraphState
from recommender.graphs.recommendation_v3.errors import RecommendationV3MissingQueryError
from recommender.graphs.recommendation_v3.models import QuerySynthesisRoutingOutcome

DEFAULT_TOP_K = 3


def create_response_generation_node(
    response_generation_agent: RecommendationV3ResponseGenerationAgent,
    top_k: int = DEFAULT_TOP_K,
) -> Callable[[RecommendationV3GraphState], dict[str, object]]:
    """Create node that generates the final conversational response using the LLM agent."""

    def response_generation_node(state: RecommendationV3GraphState) -> dict[str, object]:
        if not state.synthesized_query and state.routing_outcome == QuerySynthesisRoutingOutcome.RUN_NEW_RECOMMENDATION:
            raise RecommendationV3MissingQueryError()

        scored_recommendations = state.recommendation or []
        top_k_destinations = [r.destination for r in scored_recommendations[:top_k]]

        agent_input = RecommendationV3ResponseGenerationInput(
            user_input=state.user_input,
            outcome=state.routing_outcome,
            reason=state.routing_reason,
            synthesized_query=state.synthesized_query,
            top_k_recommendations=top_k_destinations,
        )

        result = response_generation_agent.invoke(agent_input)

        return {
            "response": result.message,
        }

    return response_generation_node
