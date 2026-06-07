from __future__ import annotations

from collections.abc import Callable


from recommender.graphs.recommendation_v2.agents.query_synthesis.query_synthesis_agent import (
    RecommendationV2SynthesizedUserRequestAgent,
)
from recommender.graphs.recommendation_v2.agents.query_synthesis.query_synthesis_agent import (
    RecommendationV2SynthesizedUserRequestInput,
)

from recommender.graphs.recommendation_v2.models import RecommendationV2GraphState
from storage.models.chat_record import ChatRecord
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def _latest_query_from_history(history: list[ChatRecord]) -> str | None:
    for row in reversed(history):
        if row.synthesized_query.strip():
            return row.synthesized_query

    return None


def create_synthesize_user_request_node(
    synthesized_user_request_agent: RecommendationV2SynthesizedUserRequestAgent,
) -> Callable[[RecommendationV2GraphState], dict[str, object]]:
    """Create node to synthesize the user request from session context."""

    def synthesize_user_request_node(
        state: RecommendationV2GraphState,
    ) -> dict[str, object]:
        if state.history is None:
            raise RuntimeError(
                "Session history must be loaded before synthesizing a recommendation_v2 user request"
            )

        previous_synthesized_query = _latest_query_from_history(state.history)
        logger.verbose(
            "Synthesizing recommendation_v2 user request for user_id=%s, session_id=%s with previous_synthesized_query=%s",
            state.session.user_id,
            state.session.session_id,
            previous_synthesized_query,
        )

        synthesized_user_request = synthesized_user_request_agent.invoke(
            RecommendationV2SynthesizedUserRequestInput(
                current_user_request=state.user_request,
                previous_synthesized_query=previous_synthesized_query,
                chat_history=state.history,
            )
        )

        logger.verbose(
            "Synthesized recommendation_v2 user request for user_id=%s, session_id=%s: query=%s",
            state.session.user_id,
            state.session.session_id,
            synthesized_user_request.synthesized_query,
        )

        return {
            "synthesized_user_request": synthesized_user_request.synthesized_query,
        }

    return synthesize_user_request_node
