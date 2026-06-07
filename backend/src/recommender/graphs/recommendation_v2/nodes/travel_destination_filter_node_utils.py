from __future__ import annotations

from pydantic import ValidationError

from recommender.graphs.recommendation_v2.filter_models import (
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
