from __future__ import annotations

from typing import Callable

from recommender.agents.recommendation_generation.recommendation_v3_generation_react_agent import (
    RecommendationV3ReActGenerationAgent,
)
from recommender.graphs.recommendation_v3.models import RecommendationV3GraphState
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def create_recommendation_generation_node(
    recommendation_v3_generation_agent: RecommendationV3ReActGenerationAgent,
) -> Callable[[RecommendationV3GraphState], dict[str, object]]:
    """Create node that generates recommendations using the tool-calling ReAct agent."""

    def recommendation_generation_node(state: RecommendationV3GraphState) -> dict[str, object]:
        query = state.synthesized_query or state.user_input
        if not query:
            logger.warning("No query available for recommendation generation")
            return {"recommendation": []}

        logger.verbose(
            "recommendation_generation_node: generating recommendations for query=%r",
            query,
        )

        recommendations = recommendation_v3_generation_agent.invoke(query)

        logger.verbose(
            "recommendation_generation_node: produced %d results",
            len(recommendations),
        )
        logger.info(
            "Recommendation generation node produced %d results",
            len(recommendations),
        )
        return {"recommendation": recommendations}

    return recommendation_generation_node
