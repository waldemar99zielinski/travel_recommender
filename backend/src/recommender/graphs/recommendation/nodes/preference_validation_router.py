from langgraph.types import Send

from recommender.graphs.recommendation.models import RecommendationGraphState
from recommender.models.data_flow.user_preferences import UserPreferences
from recommender.graphs.recommendation.nodes.response_node import create_response_node
from recommender.graphs.recommendation.nodes.recommendation_generation_node import create_recommendation_generation_node 

from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

def preference_validation_router(state: RecommendationGraphState):
    user_preferences: UserPreferences = state["extracted_preferences"]
    if user_preferences.are_preferences_present():
        logger.verbose("Preferences present. Routing to recommendation creation node.")
        return Send(create_recommendation_generation_node.__name__, state)
    else:
        logger.verbose("No preferences present. Routing to response node.")
        return Send(create_response_node.__name__, state)
