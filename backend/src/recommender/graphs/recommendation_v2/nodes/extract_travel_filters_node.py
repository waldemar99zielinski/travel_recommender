from __future__ import annotations

from collections.abc import Callable

from pydantic import ValidationError

from recommender.graphs.recommendation_v2.agents.filter_extraction.filter_extraction_agent import (
    RecommendationV2FilterExtractionAgent,
)
from recommender.graphs.recommendation_v2.agents.filter_extraction.filter_extraction_agent import (
    RecommendationV2FilterExtractionInput,
)
from recommender.graphs.recommendation_v2.filter_models import (
    RecommendationV2TravelDestinationFilter,
)
from recommender.graphs.recommendation_v2.models import RecommendationV2GraphState
from storage.models.chat_record import ChatRecord
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def _latest_filter_from_history(
    history: list[ChatRecord],
) -> RecommendationV2TravelDestinationFilter | None:
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


def create_extract_travel_filters_node(
    filter_extraction_agent: RecommendationV2FilterExtractionAgent,
) -> Callable[[RecommendationV2GraphState], dict[str, object]]:
    """Create node to extract structured catalog filters from session context."""

    def extract_travel_filters_node(
        state: RecommendationV2GraphState,
    ) -> dict[str, object]:
        if state.history is None:
            raise RuntimeError(
                "Session history must be loaded before extracting recommendation_v2 travel filters"
            )

        previous_filter = _latest_filter_from_history(state.history)
        logger.verbose(
            "Extracting recommendation_v2 travel filters for user_id=%s, session_id=%s with previous_filter=%s",
            state.session.user_id,
            state.session.session_id,
            previous_filter,
        )

        travel_destination_filter = filter_extraction_agent.invoke(
            RecommendationV2FilterExtractionInput(
                current_user_request=state.user_request,
                previous_filter=previous_filter,
                chat_history=state.history,
            )
        )

        logger.verbose(
            "Extracted recommendation_v2 travel filters for user_id=%s, session_id=%s: %s",
            state.session.user_id,
            state.session.session_id,
            travel_destination_filter,
        )

        return {
            "travel_destination_filter": travel_destination_filter,
        }

    return extract_travel_filters_node
