from __future__ import annotations

from typing import Callable

from recommender.graphs.recommendation_v0.models import RecommendationV0GraphState
from storage.stores.chat_store import ChatStore


def create_session_memory_load_node(
    recommendation_session_store: ChatStore,
) -> Callable[[RecommendationV0GraphState], dict[str, object]]:
    """Create node to load session memory from database."""

    def session_memory_load_node(
        state: RecommendationV0GraphState,
    ) -> dict[str, object]:
        persisted_rows = recommendation_session_store.load_session(
            user_id=state.session.user_id,
            session_id=state.session.session_id,
        )

        return {
            "history": persisted_rows,
        }

    return session_memory_load_node
