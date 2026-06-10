from __future__ import annotations

from collections.abc import Callable

from recommender.common.configuration import Configuration
from recommender.graphs.recommendation_v2.models import RecommendationV2
from recommender.graphs.recommendation_v2.models import RecommendationV2GraphState
from recommender.graphs.recommendation_v2.stream_events import (
    EventType,
    StreamEventRecommendation,
    emit_stream_event,
)
from recommender.graphs.recommendation_v2.utils.recommendation_generation_node_utils import (
    apply_budget_filters,
    apply_parent_region_filters,
)
from storage.stores.travel_destination_store import TravelDestinationStore
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)
configuration = Configuration()


def create_recommendation_generation_node(
    travel_destination_store: TravelDestinationStore,
) -> Callable[[RecommendationV2GraphState], dict[str, object]]:
    """Create node to generate recommendation_v2 candidates from semantic similarity."""

    def recommendation_generation_node(
        state: RecommendationV2GraphState,
    ) -> dict[str, object]:
        if state.synthesized_user_request is None:
            raise RuntimeError(
                "Synthesized user request must be generated before generating recommendation_v2 candidates"
            )

        query = state.synthesized_user_request
        keywords = state.synthesized_user_request_keywords

        logger.verbose(
            "Generating recommendation_v2 candidates for user_id=%s, session_id=%s with query=%s and keywords=%s",
            state.session.user_id,
            state.session.session_id,
            query,
            keywords,
        )

        emit_stream_event(EventType.RECOMMENDATION_GENERATION, {})

        scored_destinations = travel_destination_store.keyword_boosted_search(
            query,
            keywords=keywords,
        )

        filtered_scored_destinations = apply_parent_region_filters(
            scored_destinations,
            state.gathered_travel_destination_filter,
        )
        
        cost_statistics = travel_destination_store.cost_per_week_statistics()
        filtered_scored_destinations = apply_budget_filters(
            filtered_scored_destinations,
            state.gathered_travel_destination_filter,
            cost_statistics,
        )

        filtered_scored_destinations = filtered_scored_destinations[
            : configuration.recommendation_limit
        ]

        recommendations = [
            RecommendationV2(
                region_id=scored_destination.destination.id,
                region_name=scored_destination.destination.region,
            )
            for scored_destination in scored_destinations
        ]
        final_recommendations = [
            RecommendationV2(
                region_id=scored_destination.destination.id,
                region_name=scored_destination.destination.region,
            )
            for scored_destination in filtered_scored_destinations
        ]

        emit_stream_event(
            EventType.RECOMMENDATION,
            StreamEventRecommendation(final_recommendations).serialize(),
        )

        logger.verbose(
            "Generated %s recommendation_v2 candidates and %s final recommendations for user_id=%s, session_id=%s",
            len(recommendations),
            len(final_recommendations),
            state.session.user_id,
            state.session.session_id,
        )

        return {
            "recommendations": recommendations,
            "final_recommendations": final_recommendations,
        }

    return recommendation_generation_node
