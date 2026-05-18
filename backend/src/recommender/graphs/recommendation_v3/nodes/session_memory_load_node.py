from __future__ import annotations

from typing import Callable

from recommender.graphs.recommendation_v3.models import RecommendationV3GraphState
from storage.stores.recommendation_session_store import RecommendationSessionStore


def create_session_memory_load_node(
    recommendation_session_store: RecommendationSessionStore,
) -> Callable[[RecommendationV3GraphState], dict[str, object]]:
    """Create node to load session memory and derive the previous synthesized query."""

    def session_memory_load_node(state: RecommendationV3GraphState) -> dict[str, object]:
        persisted_rows = recommendation_session_store.load_session(
            user_id=state.session.user_id,
            session_id=state.session.session_id,
        )
        previous_synthesized_query: str | None = None
        if persisted_rows:
            latest_row = persisted_rows[-1]
            previous_synthesized_query = latest_row.query.strip() or None

        return {
            "history": persisted_rows,
            "previous_synthesized_query": previous_synthesized_query,
        }

    return session_memory_load_node
