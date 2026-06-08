from __future__ import annotations

from collections.abc import Callable

from recommender.graphs.recommendation_v2.models import RecommendationV2GraphState
from recommender.graphs.recommendation_v2.stream_events import (
    EventType,
    StreamEventTravelDestinationFilter,
    emit_stream_event,
)
from recommender.graphs.recommendation_v2.utils.travel_destination_filter_node_utils import (
    compose_travel_destination_filter,
)
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def create_gather_requirements_node() -> Callable[[RecommendationV2GraphState], dict[str, object]]:

    def gather_requirements_node(
        state: RecommendationV2GraphState,
    ) -> dict[str, object]:
        logger.verbose(
            "Gathering recommendation_v2 filters for user_id=%s, session_id=%s",
            state.session.user_id,
            state.session.session_id,
        )

        travel_destination_filter = compose_travel_destination_filter(
            extracted_parent_region_filters=state.extracted_parent_region_filters,
            extracted_direct_region_filters=state.extracted_direct_region_filters,
            extracted_seasonality_filter=state.extracted_seasonality_filter,
            extracted_budget_filter=state.extracted_budget_filter,
            fallback=state.previously_extracted_travel_destination_filter,
        )

        emit_stream_event(
            EventType.FILTER,
            StreamEventTravelDestinationFilter(
                travel_destination_filter=travel_destination_filter,
            ).serialize(),
        )

        logger.verbose(
            "Gathered recommendation_v2 filters for user_id=%s, session_id=%s: %s",
            state.session.user_id,
            state.session.session_id,
            travel_destination_filter.serialize(),
        )

        return {
            "gathered_travel_destination_filter": travel_destination_filter,
        }

    return gather_requirements_node
