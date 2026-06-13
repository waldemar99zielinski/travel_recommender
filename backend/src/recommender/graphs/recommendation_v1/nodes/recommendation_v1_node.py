from __future__ import annotations

from collections.abc import Callable

from recommender.graphs.recommendation_v1.agents.recommendation_v1_generation_react_agent import (
    RecommendationV1ReActGenerationAgent,
)
from recommender.graphs.recommendation_v1.models import RecommendationV1GraphState
from recommender.graphs.recommendation_v1.stream_events import (
    build_recommendation_event_payload,
)
from recommender.graphs.recommendation_v1.stream_events import emit_stream_event

from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

def create_recommendation_v1_node(
    recommendation_agent: RecommendationV1ReActGenerationAgent,
) -> Callable[[RecommendationV1GraphState], dict[str, object]]:
    """Create the single recommendation_v1 node handling history, agent execution, and persistence."""

    def recommendation_v1_node(state: RecommendationV1GraphState) -> dict[str, object]:

        logger.verbose(
            "Invoking recommendation_v1_node for user_id=%s, session_id=%s with user_request=%s, included_region_ids=%s, excluded_region_ids=%s, and history of %d turns",
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

        emit_stream_event(
            "recommendation",
            build_recommendation_event_payload(
                session=state.session,
                user_request=state.user_request,
                system_response=agent_result.system_response,
                recommendations=agent_result.recommendations,
                chat_history_number=len(state.history or []),
                included_regions_ids=state.included_regions_ids,
                excluded_regions_ids=state.excluded_regions_ids,
            ),
        )

        return {
            "system_response": agent_result.system_response,
            "recommendations": agent_result.recommendations,
        }

    return recommendation_v1_node
