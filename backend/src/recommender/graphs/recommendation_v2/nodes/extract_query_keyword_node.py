from __future__ import annotations

from collections.abc import Callable

from recommender.graphs.recommendation_v2.agents.query_keyword_extraction.agent import (
    RecommendationV2QueryKeywordExtractionAgent,
)
from recommender.graphs.recommendation_v2.agents.query_keyword_extraction.models import (
    RecommendationV2QueryKeywordExtractionInput,
)
from recommender.graphs.recommendation_v2.models import RecommendationV2GraphState
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def create_extract_query_keyword_node(
    query_keyword_extraction_agent: RecommendationV2QueryKeywordExtractionAgent,
) -> Callable[[RecommendationV2GraphState], dict[str, object]]:
    """Create node to extract direct-search keywords from the synthesized user request."""

    def extract_query_keyword_node(
        state: RecommendationV2GraphState,
    ) -> dict[str, object]:
        if state.synthesized_user_request is None:
            raise RuntimeError(
                "Synthesized user request must exist before extracting recommendation_v2 query keywords"
            )

        logger.verbose(
            "Extracting recommendation_v2 query keywords for user_id=%s, session_id=%s from synthesized_query=%s",
            state.session.user_id,
            state.session.session_id,
            state.synthesized_user_request,
        )

        keyword_result = query_keyword_extraction_agent.invoke(
            RecommendationV2QueryKeywordExtractionInput(
                synthesized_query=state.synthesized_user_request,
            )
        )

        logger.verbose(
            "Extracted recommendation_v2 query keywords for user_id=%s, session_id=%s: %s",
            state.session.user_id,
            state.session.session_id,
            keyword_result.keywords,
        )

        return {
            "synthesized_user_request_keywords": keyword_result.keywords,
        }

    return extract_query_keyword_node
