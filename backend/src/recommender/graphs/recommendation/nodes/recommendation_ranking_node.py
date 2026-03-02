from __future__ import annotations

from typing import Callable

from recommender.graphs.recommendation.models import RecommendationGraphState
from recommender.graphs.recommendation.models import RecommendationStatusEnum
from recommender.store.sql.travel_destination_store import SqlStore
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

def create_recommendation_ranking_node(
    sql_store: SqlStore,
) -> Callable[[RecommendationGraphState], dict[str, object] | RecommendationGraphState]:
    """Create recommendation ranking node."""

    def recommendation_ranking_node(
        state: RecommendationGraphState,
    ) -> dict[str, object] | RecommendationGraphState:
        logger.info("Ranking recommendations based on user preferences...")

        recommendations = state.recommendation or []
        # this is a safeguard - ideally we should never reach this node if there are no recommendations
        if not recommendations:
            logger.info("No recommendations found, skipping ranking.")
            return {"status": RecommendationStatusEnum.ERROR}

        logistical_preferences = state.extracted_user_logistical_preferences
        if logistical_preferences is None or not logistical_preferences.are_preferences_present():
            logger.info("No logistical preferences found, preserving semantic ranking as-is.")
            return {"status": RecommendationStatusEnum.RECOMMENDATION_GENERATED}

        ranked_recommendations = sql_store.rank_travel_destinations_by_logistical_preferences(
            recommendation=recommendations,
            logistical_preferences=logistical_preferences,
        )

        logger.info("Applied logistical re-ranking to %s recommendations.", len(ranked_recommendations))

        return {
            "recommendation": ranked_recommendations,
            "status": RecommendationStatusEnum.RECOMMENDATION_GENERATED,
        }

    return recommendation_ranking_node
