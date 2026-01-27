from recommender.graphs.recommendation.models import RecommendationGraphState
from utils.logger import get_logger

logger = get_logger(__name__)

def response_node(state: RecommendationGraphState) -> RecommendationGraphState:
    return {}
