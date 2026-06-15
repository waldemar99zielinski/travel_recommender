from __future__ import annotations

from pydantic import ValidationError

from recommender.graphs.recommendation_v2.filter_models import (
    RecommendationV2BudgetFilter,
    RecommendationV2RegionFilter,
    RecommendationV2SeasonalityFilter,
    RecommendationV2TravelDestinationFilter,
)
from storage.models.chat_record import ChatRecord
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def latest_travel_destination_filter_from_history(
    history: list[ChatRecord],
) -> RecommendationV2TravelDestinationFilter | None:
    """Return the travel-destination filter from the latest chat row only."""

    if not history:
        return None

    row = history[-1]
    try:
        return RecommendationV2TravelDestinationFilter.model_validate(
            row.travel_destination_filter or {},
        )
    except ValidationError:
        logger.warning(
            "Latest persisted travel_destination_filter is invalid for user_id=%s, session_id=%s, chat_history_number=%s",
            row.user_id,
            row.session_id,
            row.chat_history_number,
        )

    return None


def compose_travel_destination_filter(
    extracted_parent_region_filters: list[RecommendationV2RegionFilter],
    extracted_seasonality_filter: RecommendationV2SeasonalityFilter | None,
    extracted_budget_filter: RecommendationV2BudgetFilter | None,
    *,
    parent_region_filter_removed: bool = False,
    seasonality_filter_removed: bool = False,
    budget_filter_removed: bool = False,
    fallback: RecommendationV2TravelDestinationFilter | None = None,
) -> RecommendationV2TravelDestinationFilter:

    fallback_filter = fallback or RecommendationV2TravelDestinationFilter()
    parent_region_filters = (
        []
        if parent_region_filter_removed
        else extracted_parent_region_filters or fallback_filter.parent_region_filters
    )
    seasonality = fallback_filter.seasonality
    if seasonality_filter_removed:
        seasonality = RecommendationV2SeasonalityFilter()
    elif (
        extracted_seasonality_filter is not None
        and extracted_seasonality_filter.has_any_constraints()
    ):
        seasonality = extracted_seasonality_filter

    budget = fallback_filter.budget
    if budget_filter_removed:
        budget = RecommendationV2BudgetFilter()
    elif extracted_budget_filter is not None and extracted_budget_filter.has_any_constraints():
        budget = extracted_budget_filter

    return RecommendationV2TravelDestinationFilter(
        parent_region_filters=parent_region_filters,
        seasonality=seasonality,
        budget=budget,
    )


def merge_parent_region_filters(
    existing_parent_region_filters: list[RecommendationV2RegionFilter],
    updated_parent_region_filters: list[RecommendationV2RegionFilter],
) -> list[RecommendationV2RegionFilter]:
    return merge_region_filters(
        existing_parent_region_filters,
        updated_parent_region_filters,
    )


def merge_region_filters(
    existing_region_filters: list[RecommendationV2RegionFilter],
    updated_region_filters: list[RecommendationV2RegionFilter],
) -> list[RecommendationV2RegionFilter]:
    merged_filters_by_region_name = {
        region_filter.region_name: region_filter
        for region_filter in existing_region_filters
    }

    for updated_filter in updated_region_filters:
        existing_filter = merged_filters_by_region_name.get(updated_filter.region_name)
        if existing_filter is None:
            merged_filters_by_region_name[updated_filter.region_name] = updated_filter
            continue

        if updated_filter.type == "include":
            merged_filters_by_region_name[updated_filter.region_name] = updated_filter
            continue

        if existing_filter.type == "include":
            del merged_filters_by_region_name[updated_filter.region_name]
            continue

        merged_filters_by_region_name[updated_filter.region_name] = updated_filter

    return list(merged_filters_by_region_name.values())
