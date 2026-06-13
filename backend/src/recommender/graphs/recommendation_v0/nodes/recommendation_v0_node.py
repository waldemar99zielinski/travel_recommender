from __future__ import annotations

from collections.abc import Callable

from recommender.graphs.recommendation_v0.agents.recommendation_v0_generation_react_agent import (
    RecommendationV0ReActGenerationAgent,
)
from recommender.graphs.recommendation_v0.models import RecommendationV0GraphState
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def create_recommendation_v0_node(
    recommendation_agent: RecommendationV0ReActGenerationAgent,
) -> Callable[[RecommendationV0GraphState], dict[str, object]]:
    """Create the recommendation_v0 node handling agent execution."""

    def recommendation_v0_node(
        state: RecommendationV0GraphState,
    ) -> dict[str, object]:
        logger.verbose(
            "Invoking recommendation_v0_node for user_id=%s, session_id=%s with user_request=%s, included_region_ids=%s, excluded_region_ids=%s, and history of %d turns",
            state.session.user_id,
            state.session.session_id,
            state.user_request,
            state.included_regions_ids,
            state.excluded_regions_ids,
            len(state.history) if state.history else 0,
        )

        agent_result = recommendation_agent.invoke(
            user_input=state.user_request,
            included_region_ids=state.included_regions_ids,
            excluded_region_ids=state.excluded_regions_ids,
            history=state.history,
        )

        logger.verbose(
            "Agent result for user_id=%s, session_id=%s: system_response=%s, recommendations=%s",
            state.session.user_id,
            state.session.session_id,
            agent_result.system_response,
            agent_result.recommendations,
        )

        return {
            "system_response": agent_result.system_response,
            "recommendations": agent_result.recommendations,
        }

    return recommendation_v0_node
