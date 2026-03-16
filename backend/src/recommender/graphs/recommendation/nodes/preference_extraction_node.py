from __future__ import annotations

from typing import Callable

from recommender.agents.query_synthesis.recommendation_query_synthesis_agent import (
    RecommendationQuerySynthesisAgent,
    RecommendationQuerySynthesisInput,
)
from recommender.agents.preference_extraction.user_interest_preference_extraction_agent import UserInterestPreferenceExtractionAgent
from recommender.agents.preference_extraction.user_logistical_preference_extraction_agent import UserLogisticalPreferenceExtractionAgent
from recommender.graphs.recommendation.models import RecommendationGraphState, RecommendationStatusEnum
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def create_preference_extraction_node(
    recommendation_query_synthesis_agent: RecommendationQuerySynthesisAgent,
    user_interest_preference_extraction_agent: UserInterestPreferenceExtractionAgent,
    user_logistical_preference_extraction_agent: UserLogisticalPreferenceExtractionAgent,
) -> Callable[[RecommendationGraphState], dict[str, object]]:

    def preference_extraction_node(state: RecommendationGraphState) -> dict[str, object]:
        logger.verbose("Extracting user preferences from input...")

        if state.history is None:
            raise RuntimeError(
                f"Session history is not loaded in state for session_id={state.session.session_id} and user_id={state.session.user_id} when running preference extraction node"
            )

        previous_synthesized_query = state.history.latest_query()

        query_synthesis_input = RecommendationQuerySynthesisInput(
            current_user_request=state.user_input,
            previous_synthesized_query=previous_synthesized_query,
        )

        logger.verbose(
            f"Running query synthesis with current_user_request='{state.user_input}' and query_synthesis_input='{query_synthesis_input}'"
        )

        query_synthesis_result = recommendation_query_synthesis_agent.invoke(query_synthesis_input)

        logger.info("Synthesized query for extraction: %s", query_synthesis_result.synthesized_query)

        user_interests_preferences = user_interest_preference_extraction_agent.invoke(query_synthesis_result.synthesized_query)

        status = RecommendationStatusEnum.IN_PROGRESS if \
            user_interests_preferences and user_interests_preferences.are_preferences_present() \
            else RecommendationStatusEnum.NO_PREFERENCES

        logger.info("Preference extraction status: %s", status)
        logger.info("Extracted preferences: %r", user_interests_preferences)

        user_logistical_preferences = user_logistical_preference_extraction_agent.invoke(query_synthesis_result.synthesized_query)
        logger.verbose("Extracted logistical preferences: %r", user_logistical_preferences)

        return {
            "query": query_synthesis_result.synthesized_query,
            "extracted_user_interests_preferences": user_interests_preferences,
            "extracted_user_logistical_preferences": user_logistical_preferences,
            "status": status,
        }

    return preference_extraction_node
