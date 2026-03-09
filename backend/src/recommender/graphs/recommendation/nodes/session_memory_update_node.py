from __future__ import annotations

from typing import Callable

from recommender.graphs.recommendation.models import RecommendationGraphState
from recommender.models.data_flow.recommendation_session_history import RecommendationSessionHistory
from recommender.store.sql.travel_destination_store import SqlStore
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

def create_session_memory_update_node(
    sql_store: SqlStore,
) -> Callable[[RecommendationGraphState], dict[str, object]]:
    """Create node to save session memory to database."""

    def session_memory_update_node(
        state: RecommendationGraphState,
    ) -> dict[str, object]:
        user_id = state.session.user_id
        session_id = state.session.session_id

        previous_history = state.history or RecommendationSessionHistory()
        next_chat_number = previous_history.next_chat_history_number()

        synthesized_query = state.query if state.query is not None else state.user_input
        updated_query_by_chat_number = dict(previous_history.query_by_chat_number)
        updated_query_by_chat_number[next_chat_number] = synthesized_query

        updated_user_request_by_chat_number = dict(previous_history.user_request_by_chat_number)
        updated_user_request_by_chat_number[next_chat_number] = state.user_input

        updated_system_response_by_chat_number = dict(previous_history.system_response_by_chat_number)
        if state.response is not None:
            updated_system_response_by_chat_number[next_chat_number] = state.response.message

        updated_interest_preferences_by_chat_number = dict(
            previous_history.user_interest_preferences_by_chat_number,
        )
        if state.extracted_user_interests_preferences is not None:
            updated_interest_preferences_by_chat_number[next_chat_number] = state.extracted_user_interests_preferences

        updated_logistical_preferences_by_chat_number = dict(
            previous_history.user_logistical_preferences_by_chat_number,
        )
        if state.extracted_user_logistical_preferences is not None:
            updated_logistical_preferences_by_chat_number[next_chat_number] = state.extracted_user_logistical_preferences

        updated_history = RecommendationSessionHistory(
            query_by_chat_number=updated_query_by_chat_number,
            user_request_by_chat_number=updated_user_request_by_chat_number,
            system_response_by_chat_number=updated_system_response_by_chat_number,
            user_interest_preferences_by_chat_number=updated_interest_preferences_by_chat_number,
            user_logistical_preferences_by_chat_number=updated_logistical_preferences_by_chat_number,
        )

        sql_store.save_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
            history=updated_history,
        )

        return {"history": updated_history}

    return session_memory_update_node
