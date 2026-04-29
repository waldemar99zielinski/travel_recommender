from __future__ import annotations

from typing import Callable
from uuid import UUID

from recommender.graphs.recommendation.models import RecommendationGraphState
from storage.models.recommendation_session_memory import RecommendationSessionMemoryRecord
from storage.stores.recommendation_session_store import RecommendationSessionStore
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def _coerce_uuid(value: str, *, field_name: str) -> UUID:
    try:
        return UUID(value)
    except ValueError as error:
        raise ValueError(f"{field_name} must be a valid UUID") from error


def create_session_memory_update_node(
    recommendation_session_store: RecommendationSessionStore,
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
        user_request = state.user_input
        system_response = state.response if state.response is not None else ""
        interest_preference = (
            state.extracted_user_interests_preferences.model_dump()
            if state.extracted_user_interests_preferences is not None
            else {}
        )
        logistical_preference = (
            state.extracted_user_logistical_preferences.model_dump()
            if state.extracted_user_logistical_preferences is not None
            else {}
        )

        persisted_row = RecommendationSessionMemoryRecord(
            user_id=_coerce_uuid(user_id, field_name="user_id"),
            session_id=_coerce_uuid(session_id, field_name="session_id"),
            chat_history_number=next_chat_number,
            user_request=user_request,
            system_response=system_response,
            query=synthesized_query,
            interest_preference=interest_preference,
            logistical_preference=logistical_preference,
        )
        recommendation_session_store.upsert_many([persisted_row])

        updated_history = [*previous_history, persisted_row]

        return {"history": updated_history}

    return session_memory_update_node
