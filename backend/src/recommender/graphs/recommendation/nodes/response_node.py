from __future__ import annotations

from typing import Callable

from recommender.graphs.recommendation.models import RecommendationGraphState
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def create_response_node() -> Callable[[RecommendationGraphState], RecommendationGraphState]:
    """Create response node without default initialization wrappers."""

    def response_node(state: RecommendationGraphState) -> RecommendationGraphState:
        logger.warning("This is a placeholder response node. No preferences were extracted, so no recommendations can be made.")
        return {**state}

    return response_node

