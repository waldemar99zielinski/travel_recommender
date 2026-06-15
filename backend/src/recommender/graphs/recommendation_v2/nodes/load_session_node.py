from __future__ import annotations

from typing import Callable

from recommender.graphs.recommendation_v2.models import RecommendationV2GraphState
from recommender.graphs.recommendation_v2.stream_events import emit_stream_event, EventType
from recommender.graphs.recommendation_v2.utils.travel_destination_filter_node_utils import (
    latest_travel_destination_filter_from_history,
)
from storage.stores.chat_store import ChatStore
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def create_session_memory_load_node(
    chat_store: ChatStore,
) -> Callable[[RecommendationV2GraphState], dict[str, object]]:
    """Create node to load session memory from storage."""

    def session_memory_load_node(
        state: RecommendationV2GraphState,
    ) -> dict[str, object]:
        emit_stream_event(EventType.INITIALIZING, {})

        logger.verbose(
            "Loading recommendation_v2 session memory for user_id=%s, session_id=%s",
            state.session.user_id,
            state.session.session_id,
        )

        persisted_rows = chat_store.load_session(
            user_id=state.session.user_id,
            session_id=state.session.session_id,
        )

        logger.verbose(
            "Loaded %d recommendation_v2 rows for user_id=%s, session_id=%s",
            len(persisted_rows),
            state.session.user_id,
            state.session.session_id,
        )

        previous_synthesized_user_request = (
            persisted_rows[-1].synthesized_query if len(persisted_rows) > 0 else None
        )
        previously_extracted_travel_destination_filter = (
            latest_travel_destination_filter_from_history(persisted_rows)
        )

        return {
            "history": persisted_rows,
            "previous_synthesized_user_request": previous_synthesized_user_request,
            "previously_extracted_travel_destination_filter": previously_extracted_travel_destination_filter,
        }

    return session_memory_load_node
