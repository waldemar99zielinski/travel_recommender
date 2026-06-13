from __future__ import annotations

from typing import Callable

from recommender.graphs.recommendation_v0.models import RecommendationV0
from recommender.graphs.recommendation_v0.models import RecommendationV0GraphState
from storage.models.chat_record import ChatRecord
from storage.stores.chat_store import ChatStore
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def _serialize_recommendations(
    recommendations: list[RecommendationV0] | None,
) -> list[dict[str, object]]:
    if not recommendations:
        return []

    return [
        {
            "region_id": item.region_id,
            "explanation": item.explanation,
        }
        for item in recommendations
    ]


def create_session_memory_save_node(
    chat_store: ChatStore,
) -> Callable[[RecommendationV0GraphState], dict[str, object]]:
    """Create node to save session memory to database."""

    def session_memory_save_node(
        state: RecommendationV0GraphState,
    ) -> dict[str, object]:

        logger.verbose(
            "Saving session memory for user_id=%s, session_id=%s",
            state.session.user_id,
            state.session.session_id,
        )

        previous_history = state.history or []
        next_chat_number = len(previous_history)

        recommendations = _serialize_recommendations(state.recommendations)

        persisted_row = ChatRecord(
            user_id=state.session.user_id,
            session_id=state.session.session_id,
            chat_history_number=next_chat_number,
            user_request=state.user_request,
            system_response=state.system_response or "",
            synthesized_query=state.user_request,
            included_regions_ids=state.included_regions_ids,
            excluded_regions_ids=state.excluded_regions_ids,
            recommendations=recommendations,
            graph_version="v0",
        )
        chat_store.upsert_many([persisted_row])

        updated_history = [*previous_history, persisted_row]

        logger.verbose(
            "Saved row %d for user_id=%s, session_id=%s",
            next_chat_number,
            state.session.user_id,
            state.session.session_id,
        )

        return {
            "history": updated_history,
        }

    return session_memory_save_node
