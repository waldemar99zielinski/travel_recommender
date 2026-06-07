from __future__ import annotations

from collections.abc import Callable

from recommender.graphs.recommendation_v2.models import RecommendationV2
from recommender.graphs.recommendation_v2.models import RecommendationV2GraphState
from storage.stores.travel_destination_store import TravelDestinationStore
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


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

        logger.verbose(
            "Generating recommendation_v2 candidates for user_id=%s, session_id=%s with query=%s",
            state.session.user_id,
            state.session.session_id,
            query,
        )

        scored_destinations = travel_destination_store.semantic_search(query)
        recommendations = [
            RecommendationV2(
                region_id=scored_destination.destination.id,
                region_name=scored_destination.destination.region,
            )
            for scored_destination in scored_destinations
        ]

        logger.verbose(
            "Generated %s recommendation_v2 candidates for user_id=%s, session_id=%s",
            len(recommendations),
            state.session.user_id,
            state.session.session_id,
        )

        return {
            "recommendations": recommendations,
            "final_recommendations": list(recommendations),
        }

    return recommendation_generation_node
