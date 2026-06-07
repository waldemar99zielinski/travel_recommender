from __future__ import annotations

from typing import Callable

from recommender.graphs.recommendation_v2.models import RecommendationV2
from recommender.graphs.recommendation_v2.models import RecommendationV2GraphState
from recommender.graphs.recommendation_v2.stream_events import emit_stream_event
from storage.models.chat_record import ChatRecord
from storage.stores.chat_store import ChatStore
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def _serialize_recommendations(
    recommendations: list[RecommendationV2] | None,
) -> list[dict[str, object]]:
    if not recommendations:
        return []

    return [recommendation.serialize() for recommendation in recommendations]


def _serialize_travel_destination_filter(state: RecommendationV2GraphState) -> dict[str, object]:
    if state.travel_destination_filter is not None:
        return state.travel_destination_filter.serialize()

    if state.previously_extracted_travel_destination_filter is not None:
        return state.previously_extracted_travel_destination_filter.serialize()

    return {}


def create_session_memory_save_node(
    chat_store: ChatStore,
) -> Callable[[RecommendationV2GraphState], dict[str, object]]:
    """Create node to save session memory to storage."""

    def session_memory_save_node(
        state: RecommendationV2GraphState,
    ) -> dict[str, object]:
        logger.verbose(
            "Saving recommendation_v2 session memory for user_id=%s, session_id=%s",
            state.session.user_id,
            state.session.session_id,
        )

        previous_history = state.history or []
        next_chat_number = len(previous_history)

        persisted_row = ChatRecord(
            user_id=state.session.user_id,
            session_id=state.session.session_id,
            chat_history_number=next_chat_number,
            user_request=state.user_request,
            system_response=state.system_response,
            synthesized_query=state.synthesized_user_request or state.previous_synthesized_user_request,
            travel_destination_filter=_serialize_travel_destination_filter(state),
            recommendations=_serialize_recommendations(
                state.final_recommendations,
            ),
            graph_version="v2",
        )
        chat_store.upsert_many([persisted_row])

        updated_history = [*previous_history, persisted_row]

        logger.verbose(
            "Saved recommendation_v2 row %d for user_id=%s, session_id=%s",
            next_chat_number,
            state.session.user_id,
            state.session.session_id,
        )

        emit_stream_event("completed", {})

        return {
            "history": updated_history,
        }

    return session_memory_save_node
