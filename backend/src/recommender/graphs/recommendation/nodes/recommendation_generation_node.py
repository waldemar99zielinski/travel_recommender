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
        logger.verbose("Getting best matches based on user query...")

        results = travel_vector_store.search_all_ranked(state["user_input"])
        logger.verbose("Found %s ranked travel results.", len(results))

        return {
            **state,
            "recommendation": "This is a placeholder recommendation based on user preferences.",
        }

    return recommendation_generation_node
