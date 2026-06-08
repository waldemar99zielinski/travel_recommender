from __future__ import annotations

from collections.abc import Callable

from recommender.graphs.recommendation_v2.agents.response_generation.need_more_information.agent import (
    RecommendationV2NeedMoreInformationResponseGenerationAgent,
)
from recommender.graphs.recommendation_v2.agents.response_generation.need_more_information.models import (
    RecommendationV2NeedMoreInformationResponseGenerationInput,
)
from recommender.graphs.recommendation_v2.models import RecommendationV2GraphState
from recommender.graphs.recommendation_v2.stream_events import (
    EventType,
    StreamEventResponseMessage,
    build_recommendation_event_payload,
)
from recommender.graphs.recommendation_v2.stream_events import emit_stream_event
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def create_need_more_information_response_generation_node(
    response_generation_agent: RecommendationV2NeedMoreInformationResponseGenerationAgent,
) -> Callable[[RecommendationV2GraphState], dict[str, object]]:
    """Create node to generate a need-more-information response for recommendation_v2."""

    def need_more_information_response_generation_node(
        state: RecommendationV2GraphState,
    ) -> dict[str, object]:
        if state.history is None:
            raise RuntimeError(
                "Session history must be loaded before generating a need-more-information recommendation_v2 response"
            )

        logger.verbose(
            "Generating need-more-information recommendation_v2 response for user_id=%s, session_id=%s",
            state.session.user_id,
            state.session.session_id,
        )

        emit_stream_event(EventType.RESPONSE_GENERATION, {})

        response_result = response_generation_agent.invoke(
            RecommendationV2NeedMoreInformationResponseGenerationInput(
                current_user_request=state.user_request,
                chat_history=state.history,
            )
        )

        logger.verbose(
            "Generated need-more-information recommendation_v2 response for user_id=%s, session_id=%s: %s",
            state.session.user_id,
            state.session.session_id,
            response_result.response,
        )

        emit_stream_event(
            EventType.RESPONSE, StreamEventResponseMessage(response_result.response).serialize()
        )

        return {
            "system_response": response_result.response,
        }

    return need_more_information_response_generation_node
