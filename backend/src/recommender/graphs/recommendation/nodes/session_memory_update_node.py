from __future__ import annotations

from typing import Callable
from uuid import UUID

from recommender.graphs.recommendation.models import RecommendationGraphState
from storage.identifiers import normalize_identifier_to_uuid
from storage.stores.search_models import ScoredTravelDestination
from storage.models.chat_record import ChatRecord
from storage.stores.chat_store import ChatStore
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def _coerce_uuid(value: str, *, field_name: str) -> UUID:
    return normalize_identifier_to_uuid(value, field_name=field_name)


def _serialize_recommendations(
    recommendations: list[ScoredTravelDestination] | None,
) -> list[dict[str, object]]:
    if not recommendations:
        return []

    return [
        {
            "code": item.destination.id,
            "score": float(item.ranking_score),
        }
        for item in recommendations
    ]



def create_session_memory_update_node(
    recommendation_session_store: ChatStore,
) -> Callable[[RecommendationGraphState], dict[str, object]]:
    """Create node to save session memory to database."""

    def session_memory_update_node(
        state: RecommendationGraphState,
    ) -> dict[str, object]:
        user_id = state.session.user_id
        session_id = state.session.session_id

        previous_history = state.history or []
        next_chat_number = len(previous_history)

        synthesized_query = state.query if state.query is not None else state.user_input
        recommendations = _serialize_recommendations(state.recommendation)

        persisted_row = ChatRecord(
            user_id=_coerce_uuid(user_id, field_name="user_id"),
            session_id=_coerce_uuid(session_id, field_name="session_id"),
            chat_history_number=next_chat_number,
            user_request=state.user_input,
            system_response=state.response or "",
            synthesized_query=synthesized_query,
            recommendations=recommendations,
            graph_version="recommendation",
        )
        recommendation_session_store.upsert_many([persisted_row])

        updated_history = [*previous_history, persisted_row]

        return {"history": updated_history}

    return session_memory_update_node
