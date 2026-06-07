from __future__ import annotations

from collections.abc import Callable

from recommender.graphs.recommendation_v2.agents.filter_extraction.regions.agent import (
    RecommendationV2RegionsFilterExtractionAgent,
)
from recommender.graphs.recommendation_v2.agents.filter_extraction.regions.models import (
    RecommendationV2RegionsFilterExtractionInput,
)
from recommender.graphs.recommendation_v2.filter_models import (
    RecommendationV2RegionFilter,
    RecommendationV2TravelDestinationFilter,
)
from recommender.graphs.recommendation_v2.models import RecommendationV2GraphState
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def _resolve_previously_extracted_travel_destination_filter(
    state: RecommendationV2GraphState,
) -> RecommendationV2TravelDestinationFilter:
    if state.previously_extracted_travel_destination_filter is not None:
        return state.previously_extracted_travel_destination_filter

    return RecommendationV2TravelDestinationFilter()
def _request_region_filters(
    *,
    included_regions_ids_from_request: list[str],
    excluded_regions_ids_from_request: list[str],
) -> list[RecommendationV2RegionFilter]:
    request_region_filters: list[RecommendationV2RegionFilter] = []

    # Explicit request IDs represent direct region picks, so they map to the `region` field.
    for region_name in included_regions_ids_from_request:
        request_region_filters.append(
            RecommendationV2RegionFilter(
                field_name="region",
                region_name=region_name,
                type="include",
            )
        )

    for region_name in excluded_regions_ids_from_request:
        request_region_filters.append(
            RecommendationV2RegionFilter(
                field_name="region",
                region_name=region_name,
                type="exclude",
            )
        )

    return request_region_filters


def _merge_region_filters_with_priority(
    *,
    base_regions: list[RecommendationV2RegionFilter],
    overriding_regions: list[RecommendationV2RegionFilter],
) -> list[RecommendationV2RegionFilter]:
    merged_regions: dict[tuple[str, str], RecommendationV2RegionFilter] = {
        (region.field_name, region.region_name): region
        for region in base_regions
    }

    for region in overriding_regions:
        merged_regions[(region.field_name, region.region_name)] = region

    return list(merged_regions.values())


def create_extract_regions_filter_node(
    regions_filter_extraction_agent: RecommendationV2RegionsFilterExtractionAgent,
) -> Callable[[RecommendationV2GraphState], dict[str, object]]:
    """Create node to extract recommendation_v2 region filters from the current turn."""

    def extract_regions_filter_node(
        state: RecommendationV2GraphState,
    ) -> dict[str, object]:
        previously_extracted_travel_destination_filter = (
            _resolve_previously_extracted_travel_destination_filter(state)
        )

        logger.verbose(
            "Extracting recommendation_v2 region filters for user_id=%s, session_id=%s with previous_regions=%s, included_regions_ids_from_request=%s, excluded_regions_ids_from_request=%s",
            state.session.user_id,
            state.session.session_id,
            previously_extracted_travel_destination_filter.regions,
            state.included_regions_ids_from_request,
            state.excluded_regions_ids_from_request,
        )

        regions_result = regions_filter_extraction_agent.invoke(
            RecommendationV2RegionsFilterExtractionInput(
                current_user_request=state.user_request,
            )
        )
        request_region_filters = _request_region_filters(
            included_regions_ids_from_request=state.included_regions_ids_from_request,
            excluded_regions_ids_from_request=state.excluded_regions_ids_from_request,
        )
        merged_regions = _merge_region_filters_with_priority(
            base_regions=regions_result.regions or [],
            overriding_regions=request_region_filters,
        )
        logger.verbose(
            "Extracted recommendation_v2 region filters for user_id=%s, session_id=%s: %s",
            state.session.user_id,
            state.session.session_id,
            merged_regions,
        )

        return {
            "extracted_region_filters": merged_regions,
        }

    return extract_regions_filter_node
