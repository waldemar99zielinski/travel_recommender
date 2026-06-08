from __future__ import annotations

from collections.abc import Callable

from pydantic import ValidationError

from recommender.graphs.recommendation_v2.agents.filter_extraction.parent_region.agent import (
    RecommendationV2ParentRegionFilterExtractionAgent,
)
from recommender.graphs.recommendation_v2.agents.filter_extraction.parent_region.models import (
    RecommendationV2ParentRegionFilterExtractionInput,
)
from recommender.graphs.recommendation_v2.filter_models import (
    ALLOWED_RECOMMENDATION_V2_PARENT_REGION_NAMES,
    RecommendationV2RegionFilter,
)
from recommender.graphs.recommendation_v2.models import RecommendationV2GraphState
from recommender.graphs.recommendation_v2.utils.travel_destination_filter_node_utils import (
    merge_parent_region_filters,
)
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

_ALLOWED_PARENT_REGION_SET = frozenset(ALLOWED_RECOMMENDATION_V2_PARENT_REGION_NAMES)


def create_extract_parent_region_filter_node(
    parent_region_filter_extraction_agent: RecommendationV2ParentRegionFilterExtractionAgent,
) -> Callable[[RecommendationV2GraphState], dict[str, object]]:
    """Create node to extract parent-region filters from the current turn."""

    def extract_parent_region_filter_node(
        state: RecommendationV2GraphState,
    ) -> dict[str, object]:
        logger.verbose(
            "Extracting recommendation_v2 parent-region filters for user_id=%s, session_id=%s",
            state.session.user_id,
            state.session.session_id,
        )

        result = parent_region_filter_extraction_agent.invoke(
            RecommendationV2ParentRegionFilterExtractionInput(
                current_user_request=state.user_request,
            )
        )

        extracted_filters: list[RecommendationV2RegionFilter] = []
        if result.parent_regions:
            for entry in result.parent_regions:
                if entry.name not in _ALLOWED_PARENT_REGION_SET:
                    logger.warning(
                        "Skipping invalid parent_region from LLM output: %s",
                        entry.name,
                    )
                    continue
                try:
                    extracted_filters.append(
                        RecommendationV2RegionFilter(
                            field_name="parent_region",
                            region_name=entry.name,
                            type=entry.type,
                        )
                    )
                except ValidationError:
                    logger.warning(
                        "Skipping invalid parent_region filter from LLM output: %s",
                        entry.model_dump(),
                    )

        existing_filters = []
        if state.previously_extracted_travel_destination_filter is not None:
            existing_filters = (
                state.previously_extracted_travel_destination_filter.parent_region_filters
            )
        valid_filters = merge_parent_region_filters(existing_filters, extracted_filters)

        logger.verbose(
            "Extracted recommendation_v2 parent-region filters for user_id=%s, session_id=%s: %s",
            state.session.user_id,
            state.session.session_id,
            valid_filters,
        )

        return {
            "extracted_parent_region_filters": valid_filters,
        }

    return extract_parent_region_filter_node
