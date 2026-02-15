from __future__ import annotations

from typing import Callable

from recommender.embeddings.travel_vector_store import TravelVectorStore
from recommender.graphs.recommendation.models import RecommendationGraphState
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

def create_recommendation_generation_node(
    travel_vector_store: TravelVectorStore,
) -> Callable[[RecommendationGraphState], RecommendationGraphState]:
    """Create recommendation node with an injected vector store dependency."""

    def recommendation_generation_node(
        state: RecommendationGraphState,
    ) -> RecommendationGraphState:
        logger.info("Getting best matches based on user query...")

        user_input = state.user_input

        logger.verbose("Searching travel vector store with user input: %s", user_input)

        results = travel_vector_store.search_all_ranked(user_input)
        logger.info("Found %s ranked travel results.", len(results))

        return {
            "recommendation": results,
        }

    return recommendation_generation_node
