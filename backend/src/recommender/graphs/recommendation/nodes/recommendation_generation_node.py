from __future__ import annotations

from typing import Callable

from recommender.graphs.recommendation.models import RecommendationGraphState
from storage.stores.travel_destination_store import TravelDestinationStore
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def create_recommendation_generation_node(
    travel_destination_store: TravelDestinationStore,
) -> Callable[[RecommendationGraphState], dict[str, object]]:
    """Create recommendation node with an injected travel destination store."""

    def recommendation_generation_node(
        state: RecommendationGraphState,
    ) -> dict[str, object]:
        logger.info("Getting best matches based on user query...")

        query = state.query if state.query is not None else state.user_input

        logger.verbose("Searching travel store with query: %s", query)

        results = travel_destination_store.semantic_search(query)
        logger.info("Found %s ranked travel results.", len(results))

        return {
            "recommendation": results,
        }

    return recommendation_generation_node
