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
    """Return the latest valid persisted travel-destination filter from chat history."""

    for row in reversed(history):
        if not row.travel_destination_filter:
            continue

        try:
            return RecommendationV2TravelDestinationFilter.model_validate(
                row.travel_destination_filter,
            )
        except ValidationError:
            logger.warning(
                "Skipping invalid persisted travel_destination_filter for user_id=%s, session_id=%s, chat_history_number=%s",
                row.user_id,
                row.session_id,
                row.chat_history_number,
            )

    return None


def compose_travel_destination_filter(
    extracted_parent_region_filters: list[RecommendationV2RegionFilter],
    extracted_direct_region_filters: list[RecommendationV2RegionFilter],
    extracted_seasonality_filter: RecommendationV2SeasonalityFilter | None,
    extracted_budget_filter: RecommendationV2BudgetFilter | None,
    *,
    fallback: RecommendationV2TravelDestinationFilter | None = None,
) -> RecommendationV2TravelDestinationFilter:

    fallback_filter = fallback or RecommendationV2TravelDestinationFilter()
    has_seasonality = (
        extracted_seasonality_filter is not None
        and extracted_seasonality_filter.has_any_constraints()
    )
    has_budget = (
        extracted_budget_filter is not None
        and extracted_budget_filter.has_any_constraints()
    )

    return RecommendationV2TravelDestinationFilter(
        parent_region_filters=(
            extracted_parent_region_filters or fallback_filter.parent_region_filters
        ),
        direct_region_filters=(
            extracted_direct_region_filters or fallback_filter.direct_region_filters
        ),
        seasonality=(
            extracted_seasonality_filter if has_seasonality else fallback_filter.seasonality
        ),
        budget=(
            extracted_budget_filter if has_budget else fallback_filter.budget
        ),
    )
