from __future__ import annotations

from typing import Literal

from recommender.graphs.recommendation.models import RecommendationGraphState
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

ROUTE_RECOMMENDATION_GENERATION = "recommendation_generation"
ROUTE_RESPONSE = "response"

PreferenceValidationRoute = Literal[
    "recommendation_generation",
    "response",
]

def preference_validation_router(state: RecommendationGraphState) -> PreferenceValidationRoute:
    user_interests_preferences = state.extracted_user_interests_preferences

    if user_interests_preferences is None or not user_interests_preferences.are_preferences_present():
        logger.verbose("No extracted preferences in state. Routing directly to response node.")
        return ROUTE_RESPONSE

    logger.verbose("Preferences present. Routing to recommendation generation node.")
    return ROUTE_RECOMMENDATION_GENERATION
