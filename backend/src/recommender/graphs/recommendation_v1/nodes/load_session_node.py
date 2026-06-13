from __future__ import annotations

from typing import Callable

from recommender.graphs.recommendation_v1.models import RecommendationV1GraphState
from recommender.graphs.recommendation_v1.stream_events import emit_stream_event
from storage.stores.chat_store import ChatStore
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def create_session_memory_load_node(
    chat_store: ChatStore,
) -> Callable[[RecommendationV1GraphState], dict[str, object]]:
    """Create node to load session memory from database."""

    def session_memory_load_node(
        state: RecommendationV1GraphState,
    ) -> dict[str, object]:
        emit_stream_event("init", {})

        logger.verbose(
            "Loading session memory for user_id=%s, session_id=%s",
            state.session.user_id,
            state.session.session_id,
        )

        persisted_rows = chat_store.load_session(
            user_id=state.session.user_id,
            session_id=state.session.session_id,
        )

        logger.verbose(
            "Loaded %d rows for user_id=%s, session_id=%s",
            len(persisted_rows),
            state.session.user_id,
            state.session.session_id,
        )

        return {
            "history": persisted_rows,
        }

    return session_memory_load_node
