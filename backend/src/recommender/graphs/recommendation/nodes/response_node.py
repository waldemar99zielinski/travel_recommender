from __future__ import annotations

from typing import Callable 

from recommender.graphs.recommendation.models import RecommendationGraphState
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def create_response_node() -> Callable[[RecommendationGraphState], RecommendationGraphState]:
    """Create final response node for all graph exits."""

    def response_node(state: RecommendationGraphState) -> RecommendationGraphState:
        # TOOD implement response agent that will create natural language response based on extracted preferences.

        logger.warning("Response node placeholder.")

        return {}

    return response_node
