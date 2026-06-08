from __future__ import annotations

from collections.abc import Callable

from recommender.graphs.recommendation_v2.agents.request_routing.request_routing_agent import (
    RecommendationV2RequestRoutingAgent,
)
from recommender.graphs.recommendation_v2.agents.request_routing.request_routing_agent import (
    RecommendationV2RequestRoutingInput,
)
from recommender.graphs.recommendation_v2.models import RecommendationV2GraphState
from recommender.graphs.recommendation_v2.stream_events import emit_stream_event, EventType
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def create_request_routing_node(
    request_routing_agent: RecommendationV2RequestRoutingAgent,
) -> Callable[[RecommendationV2GraphState], dict[str, object]]:
    """Create node to classify how recommendation_v2 should handle the current turn."""

    def request_routing_node(
        state: RecommendationV2GraphState,
    ) -> dict[str, object]:
        if state.history is None:
            raise RuntimeError(
                "Session history must be loaded before routing a recommendation_v2 user request"
            )

        logger.verbose(
            "Routing recommendation_v2 request for user_id=%s, session_id=%s",
            state.session.user_id,
            state.session.session_id,
        )

        emit_stream_event(EventType.VALIDATING_REQUEST, {})

        routing_result = request_routing_agent.invoke(
            RecommendationV2RequestRoutingInput(
                current_user_request=state.user_request,
                chat_history=state.history,
            )
        )

        if routing_result.decision == "new_recommendation_run":
            emit_stream_event(EventType.GATHERING_FILTER, {})

        logger.verbose(
            "Routed recommendation_v2 request for user_id=%s, session_id=%s to %s",
            state.session.user_id,
            state.session.session_id,
            routing_result.decision,
        )

        return {
            "request_routing_decision": routing_result.decision,
            "request_routing_reason": routing_result.reason,
        }

    return request_routing_node
