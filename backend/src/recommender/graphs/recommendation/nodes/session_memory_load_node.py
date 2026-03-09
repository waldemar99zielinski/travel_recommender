from __future__ import annotations

from typing import Callable

from recommender.graphs.recommendation.models import RecommendationGraphState
from recommender.store.sql.travel_destination_store import SqlStore


def create_session_memory_load_node(
    sql_store: SqlStore,
) -> Callable[[RecommendationGraphState], dict[str, object]]:
    """Create node to load session memory from database."""

    def session_memory_load_node(
        state: RecommendationGraphState,
    ) -> dict[str, object]:
        user_id = state.session.user_id
        session_id = state.session.session_id

        history = sql_store.load_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
        )

        return {
            "history": history,
        }

    return session_memory_load_node
