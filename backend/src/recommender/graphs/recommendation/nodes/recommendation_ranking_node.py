from __future__ import annotations

from typing import Callable

from sqlalchemy import case
from sqlalchemy import func
from sqlalchemy import literal
from sqlmodel import col
from sqlmodel import Session
from sqlmodel import select

from recommender.graphs.recommendation.models import RecommendationGraphState
from recommender.models.data_flow.recommendation_output import Recommendation
from recommender.models.data_flow.user_preferences import UserLogisticalPreferences
from recommender.store.sql.travel_destination_store import SqlStore
from recommender.store.sql.travel_destination_table import TravelDestinationTable
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

SEASON_TO_MONTHS = {
    "winter": ("dec", "jan", "feb"),
    "spring": ("mar", "apr", "may"),
    "summer": ("jun", "jul", "aug"),
    "autumn": ("sep", "oct", "nov"),
    "fall": ("sep", "oct", "nov"),
}


def create_recommendation_ranking_node(
    sql_store: SqlStore,
) -> Callable[[RecommendationGraphState], RecommendationGraphState]:
    """Create recommendation ranking node."""

    def recommendation_ranking_node(
        state: RecommendationGraphState,
    ) -> RecommendationGraphState:
        logger.info("Ranking recommendations based on user preferences...")

        recommendations = state.recommendation or []
        if not recommendations:
            logger.info("No recommendations found, skipping ranking.")
            return state

        logistical_preferences = state.extracted_user_logistical_preferences
        if logistical_preferences is None or not logistical_preferences.are_preferences_present():
            logger.info("No logistical preferences found, preserving semantic ranking as-is.")
            return state



        logger.info("Applied logistical re-ranking to %s recommendations.", len(recommendations))

        return {
            #TODO put the ranked recommendations here
        }

    return recommendation_ranking_node
