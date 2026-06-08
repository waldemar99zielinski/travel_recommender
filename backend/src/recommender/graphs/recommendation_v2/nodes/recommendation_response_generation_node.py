from __future__ import annotations

from collections.abc import Callable

from recommender.graphs.recommendation_v2.agents.response_generation.no_results_for_recommendation.agent import (
    RecommendationV2NoResultsForRecommendationResponseGenerationAgent,
)
from recommender.graphs.recommendation_v2.agents.response_generation.no_results_for_recommendation.models import (
    RecommendationV2NoResultsForRecommendationResponseGenerationInput,
)
from recommender.graphs.recommendation_v2.agents.response_generation.recommendation_generated.agent import (
    RecommendationV2RecommendationGeneratedResponseGenerationAgent,
)
from recommender.graphs.recommendation_v2.agents.response_generation.recommendation_generated.models import (
    RecommendationV2RecommendationGeneratedResponseGenerationInput,
)
from recommender.graphs.recommendation_v2.models import RecommendationV2GraphState
from recommender.graphs.recommendation_v2.utils.travel_destination_filter_node_utils import (
    compose_travel_destination_filter,
)
from recommender.graphs.recommendation_v2.stream_events import (
    EventType,
    StreamEventResponseMessage,
    build_recommendation_event_payload,
)
from recommender.graphs.recommendation_v2.stream_events import emit_stream_event
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def create_recommendation_response_generation_node(
    recommendation_generated_agent: RecommendationV2RecommendationGeneratedResponseGenerationAgent,
    no_results_agent: RecommendationV2NoResultsForRecommendationResponseGenerationAgent,
) -> Callable[[RecommendationV2GraphState], dict[str, object]]:
    """Create node to generate a recommendation response for recommendation_v2."""

    def recommendation_response_generation_node(
        state: RecommendationV2GraphState,
    ) -> dict[str, object]:
        if state.history is None:
            raise RuntimeError(
                "Session history must be loaded before generating a recommendation_v2 recommendation response"
            )

        logger.verbose(
            "Generating recommendation_v2 recommendation response for user_id=%s, session_id=%s with final_recommendations_count=%s",
            state.session.user_id,
            state.session.session_id,
            len(state.final_recommendations) if state.final_recommendations is not None else None,
        )

        emit_stream_event(EventType.RESPONSE_GENERATION, {})

        travel_destination_filter = compose_travel_destination_filter(
            extracted_parent_region_filters=state.extracted_parent_region_filters,
            extracted_direct_region_filters=state.extracted_direct_region_filters,
            extracted_seasonality_filter=state.extracted_seasonality_filter,
            extracted_budget_filter=state.extracted_budget_filter,
            fallback=state.previously_extracted_travel_destination_filter,
        )

        if state.final_recommendations and len(state.final_recommendations) > 0:
            response_result = recommendation_generated_agent.invoke(
                RecommendationV2RecommendationGeneratedResponseGenerationInput(
                    current_user_request=state.user_request,
                    synthesized_user_request=state.synthesized_user_request,
                    travel_destination_filter=travel_destination_filter,
                    recommendations=state.final_recommendations,
                    chat_history=state.history,
                )
            )
        else:
            response_result = no_results_agent.invoke(
                RecommendationV2NoResultsForRecommendationResponseGenerationInput(
                    current_user_request=state.user_request,
                    synthesized_user_request=state.synthesized_user_request,
                    travel_destination_filter=travel_destination_filter,
                    recommendations=state.recommendations,
                    final_recommendations=state.final_recommendations,
                    chat_history=state.history,
                )
            )

        logger.verbose(
            "Generated recommendation_v2 recommendation response for user_id=%s, session_id=%s: %s",
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

    return recommendation_response_generation_node
