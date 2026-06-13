from __future__ import annotations

from typing import Callable

from recommender.graphs.recommendation.models import RecommendationGraphState
from storage.stores.chat_store import ChatStore


def create_session_memory_load_node(
    recommendation_session_store: ChatStore,
) -> Callable[[RecommendationGraphState], dict[str, object]]:
    """Create node to load session memory from database."""

    def session_memory_load_node(
        state: RecommendationGraphState,
    ) -> dict[str, object]:
        user_id = state.session.user_id
        session_id = state.session.session_id

        persisted_rows = recommendation_session_store.load_session(
            user_id=user_id,
            session_id=session_id,
        )

        return {
            "history": persisted_rows,
        }

    return session_memory_load_node
