from recommender.agents.preference_extraction.preference_extraction_agent import PreferenceExtractionAgent
from recommender.graphs.recommendation.models import RecommendationGraphState
from utils.logger import get_logger

logger = get_logger(__name__)

def preference_extraction_node(state: RecommendationGraphState) -> RecommendationGraphState:
    logger.verbose("Extracting user preferences from input...")

    agent = PreferenceExtractionAgent.builder().build()
    user_preferences = agent.invoke(state["user_input"])

    logger.info("Extracted preferences: %r", user_preferences)

    return RecommendationGraphState(extracted_preferences=user_preferences)