from __future__ import annotations

from collections.abc import Callable

from pydantic import ValidationError

from recommender.graphs.recommendation_v2.agents.filter_extraction.direct_region.agent import (
    RecommendationV2DirectRegionFilterExtractionAgent,
)
from recommender.graphs.recommendation_v2.agents.filter_extraction.direct_region.models import (
    RecommendationV2DirectRegionFilterExtractionInput,
)
from recommender.graphs.recommendation_v2.filter_models import (
    ALLOWED_RECOMMENDATION_V2_REGION_NAMES,
    RecommendationV2RegionFilter,
)
from recommender.graphs.recommendation_v2.models import RecommendationV2GraphState
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

_ALLOWED_DIRECT_REGION_SET = frozenset(ALLOWED_RECOMMENDATION_V2_REGION_NAMES)


def create_extract_direct_region_filter_node(
    direct_region_filter_extraction_agent: RecommendationV2DirectRegionFilterExtractionAgent,
) -> Callable[[RecommendationV2GraphState], dict[str, object]]:
    """Create node to extract direct-region filters from the current turn."""

    def extract_direct_region_filter_node(
        state: RecommendationV2GraphState,
    ) -> dict[str, object]:
        logger.verbose(
            "Extracting recommendation_v2 direct-region filters for user_id=%s, session_id=%s",
            state.session.user_id,
            state.session.session_id,
        )

        result = direct_region_filter_extraction_agent.invoke(
            RecommendationV2DirectRegionFilterExtractionInput(
                current_user_request=state.user_request,
            )
        )

        valid_filters: list[RecommendationV2RegionFilter] = []
        if result.regions:
            for entry in result.regions:
                if entry.name not in _ALLOWED_DIRECT_REGION_SET:
                    logger.warning(
                        "Skipping invalid direct region from LLM output: %s",
                        entry.name,
                    )
                    continue
                try:
                    valid_filters.append(
                        RecommendationV2RegionFilter(
                            field_name="region",
                            region_name=entry.name,
                            type=entry.type,
                        )
                    )
                except ValidationError:
                    logger.warning(
                        "Skipping invalid direct region filter from LLM output: %s",
                        entry.model_dump(),
                    )

        logger.verbose(
            "Extracted recommendation_v2 direct-region filters for user_id=%s, session_id=%s: %s",
            state.session.user_id,
            state.session.session_id,
            valid_filters,
        )

        return {
            "extracted_direct_region_filters": valid_filters,
        }

    return extract_direct_region_filter_node
