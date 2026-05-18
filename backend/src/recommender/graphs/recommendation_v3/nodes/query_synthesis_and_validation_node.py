from __future__ import annotations

from typing import Any
from typing import Callable

from recommender.agents.query_synthesis_and_validation.query_synthesis_and_validation_agent import (
    RecommendationQuerySynthesisAndValidationAgent,
)
from recommender.agents.query_synthesis_and_validation.query_synthesis_and_validation_agent import (
    RecommendationQuerySynthesisAndValidationInput,
)
from recommender.graphs.recommendation_v3.errors import RecommendationV3EmptyUserInputError
from recommender.graphs.recommendation_v3.models import RecommendationV3GraphState
from utils.logger import LoggerManager

logger: Any = LoggerManager.get_logger(__name__)


def _format_chat_history(state: RecommendationV3GraphState) -> str:
    if not state.history:
        return "None"

    parts: list[str] = []
    for row in state.history:
        parts.append(
            "User: "
            f"{row.user_request.strip() or 'None'}\n"
            "Assistant: "
            f"{row.system_response.strip() or 'None'}"
        )

    return "\n\n".join(parts)


def create_query_synthesis_and_validation_node(
    query_synthesis_and_validation_agent: RecommendationQuerySynthesisAndValidationAgent,
) -> Callable[[RecommendationV3GraphState], dict[str, object]]:
    """Create node that synthesizes the query and validates the next graph outcome."""

    def query_synthesis_and_validation_node(state: RecommendationV3GraphState) -> dict[str, object]:
        user_input = state.user_input.strip()

        if not user_input:
            raise RecommendationV3EmptyUserInputError()

        logger.verbose(
            "query_synthesis_and_validation_node: input=%r, previous_query=%r, history_rows=%d",
            user_input,
            state.previous_synthesized_query,
            len(state.history or []),
        )

        validation_result = query_synthesis_and_validation_agent.invoke(
            RecommendationQuerySynthesisAndValidationInput(
                current_user_input=user_input,
                previous_synthesized_query=state.previous_synthesized_query,
                chat_history=_format_chat_history(state),
            )
        )

        logger.verbose(
            "query_synthesis_and_validation_node: route=%s, synthesized_query=%r, reason=%r",
            validation_result.route,
            validation_result.synthesized_query,
            validation_result.reason,
        )

        return {
            "synthesized_query": validation_result.synthesized_query,
            "routing_outcome": validation_result.route,
            "routing_reason": validation_result.reason,
        }

    return query_synthesis_and_validation_node
