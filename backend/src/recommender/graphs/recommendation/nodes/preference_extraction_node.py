from __future__ import annotations

from typing import Callable

from recommender.agents.preference_extraction.preference_extraction_agent import PreferenceExtractionAgent
from recommender.graphs.recommendation.models import RecommendationGraphState
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def create_preference_extraction_node(
    preference_extraction_agent: PreferenceExtractionAgent,
) -> Callable[[RecommendationGraphState], RecommendationGraphState]:
    def preference_extraction_node(state: RecommendationGraphState) -> RecommendationGraphState:
        logger.verbose("Extracting user preferences from input...")

        user_preferences = preference_extraction_agent.invoke(state["user_input"])

        logger.info("Extracted preferences: %r", user_preferences)

        return {**state, "extracted_preferences": user_preferences}

    return preference_extraction_node
