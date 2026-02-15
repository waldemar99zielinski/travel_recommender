from __future__ import annotations

from typing import Callable

from recommender.agents.preference_extraction.preference_extraction_agent import PreferenceExtractionAgent
from recommender.graphs.recommendation.models import RecommendationGraphState, RecommendationStatusEnum
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def create_preference_extraction_node(
    preference_extraction_agent: PreferenceExtractionAgent,
) -> Callable[[RecommendationGraphState], RecommendationGraphState]:

    def preference_extraction_node(state: RecommendationGraphState) -> RecommendationGraphState:
        logger.verbose("Extracting user preferences from input...")

        user_preferences = preference_extraction_agent.invoke(state.user_input)

        status = RecommendationStatusEnum.IN_PROGRESS if \
            user_preferences and user_preferences.are_preferences_present \
            else RecommendationStatusEnum.NO_PREFERENCES

        logger.info("Preference extraction status: %s", status)
        logger.info("Extracted preferences: %r", user_preferences)

        return {
            "extracted_preferences": user_preferences,
            "status": status,
        }

    return preference_extraction_node
