from __future__ import annotations

from typing import Any
from typing import Callable
from uuid import UUID

from recommender.graphs.recommendation_v3.models import RecommendationV3GraphState
from storage.identifiers import normalize_identifier_to_uuid
from storage.models.recommendation_session_memory import RecommendationSessionMemoryRecord
from storage.stores.recommendation_session_store import RecommendationSessionStore
from utils.logger import LoggerManager

logger: Any = LoggerManager.get_logger(__name__)


def _coerce_uuid(value: str, *, field_name: str) -> UUID:
    return normalize_identifier_to_uuid(value, field_name=field_name)


def create_session_memory_update_node(
    recommendation_session_store: RecommendationSessionStore,
) -> Callable[[RecommendationV3GraphState], dict[str, object]]:
    """Create placeholder node to persist the final state of one recommendation_v3 turn."""

    def _serialize_system_messages(response: str) -> list[dict[str, object]]:
        if not response.strip():
            return []

        return [
            {
                "type": "text",
                "context": {
                    "text": response,
                },
            }
        ]

    def session_memory_update_node(state: RecommendationV3GraphState) -> dict[str, object]:
        previous_history = state.history or []
        persisted_row = RecommendationSessionMemoryRecord(
            user_id=_coerce_uuid(state.session.user_id, field_name="user_id"),
            session_id=_coerce_uuid(state.session.session_id, field_name="session_id"),
            chat_history_number=len(previous_history),
            user_request=state.user_input,
            system_response=state.response or "",
            system_messages=_serialize_system_messages(state.response or ""),
            query=state.synthesized_query or state.user_input,
        )
        recommendation_session_store.upsert_many([persisted_row])

        logger.verbose(
            "session_memory_update_node: persisted turn %d, response_length=%d, query=%r",
            len(previous_history),
            len(state.response or ""),
            persisted_row.query,
        )

        return {"history": [*previous_history, persisted_row]}

    return session_memory_update_node
