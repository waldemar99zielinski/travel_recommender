from __future__ import annotations

from collections.abc import Callable

from recommender.graphs.recommendation_v2.agents.response_generation.out_of_scope.agent import (
    RecommendationV2OutOfScopeResponseGenerationAgent,
)
from recommender.graphs.recommendation_v2.agents.response_generation.out_of_scope.models import (
    RecommendationV2OutOfScopeResponseGenerationInput,
)
from recommender.graphs.recommendation_v2.models import RecommendationV2GraphState
from recommender.graphs.recommendation_v2.stream_events import (
    build_recommendation_event_payload,
)
from recommender.graphs.recommendation_v2.stream_events import emit_stream_event
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def create_out_of_scope_response_generation_node(
    response_generation_agent: RecommendationV2OutOfScopeResponseGenerationAgent,
) -> Callable[[RecommendationV2GraphState], dict[str, object]]:
    """Create node to generate an out-of-scope response for recommendation_v2."""

    def out_of_scope_response_generation_node(
        state: RecommendationV2GraphState,
    ) -> dict[str, object]:
        if state.history is None:
            raise RuntimeError(
                "Session history must be loaded before generating an out-of-scope recommendation_v2 response"
            )

        logger.verbose(
            "Generating out-of-scope recommendation_v2 response for user_id=%s, session_id=%s",
            state.session.user_id,
            state.session.session_id,
        )

        response_result = response_generation_agent.invoke(
            RecommendationV2OutOfScopeResponseGenerationInput(
                current_user_request=state.user_request,
                chat_history=state.history,
            )
        )

        logger.verbose(
            "Generated out-of-scope recommendation_v2 response for user_id=%s, session_id=%s: %s",
            state.session.user_id,
            state.session.session_id,
            response_result.response,
        )

        emit_stream_event(
            "recommendation",
            build_recommendation_event_payload(
                session=state.session,
                user_request=state.user_request,
                system_response=response_result.response,
                recommendations=state.final_recommendations or state.recommendations,
                chat_history_number=len(state.history or []),
            ),
        )

        return {
            "system_response": response_result.response,
        }

    return out_of_scope_response_generation_node
