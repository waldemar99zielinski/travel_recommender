from __future__ import annotations

from recommender.models.data_flow.recommendation_session_history import RecommendationSessionHistory
from recommender.models.data_flow.user_preferences import UserInterestPreferences
from recommender.models.data_flow.user_preferences import UserLogisticalPreferences
from recommender.store.sql.tables.recommendation_session_memory_table import (
    RecommendationSessionMemoryTable,
)
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)
VERBOSE = 15

class RecommendationSessionMemoryTableMapper:
    """Maps between RecommendationSessionHistory and RecommendationSessionMemoryTable."""

    def to_tables(
        self,
        user_id: str,
        session_id: str,
        history: RecommendationSessionHistory,
    ) -> list[RecommendationSessionMemoryTable]:
        """Convert RecommendationSessionHistory to multiple RecommendationSessionMemoryTable rows."""
        tables: list[RecommendationSessionMemoryTable] = []

        all_chat_numbers: set[int] = set(history.query_by_chat_number)
        all_chat_numbers.update(history.user_request_by_chat_number)
        all_chat_numbers.update(history.system_response_by_chat_number)
        all_chat_numbers.update(history.user_interest_preferences_by_chat_number)
        all_chat_numbers.update(history.user_logistical_preferences_by_chat_number)

        for chat_number in sorted(all_chat_numbers):
            user_request = history.user_request_by_chat_number.get(chat_number, "")
            system_response = history.system_response_by_chat_number.get(chat_number, "")
            query = history.query_by_chat_number.get(chat_number, "")
            interest_pref = history.user_interest_preferences_by_chat_number.get(chat_number)
            logistical_pref = history.user_logistical_preferences_by_chat_number.get(chat_number)

            interest_json = (
                interest_pref.model_dump_json()
                if interest_pref and interest_pref.are_preferences_present()
                else "{}"
            )
            logistical_json = (
                logistical_pref.model_dump_json()
                if logistical_pref and logistical_pref.are_preferences_present()
                else "{}"
            )

            tables.append(
                RecommendationSessionMemoryTable(
                    user_id=user_id,
                    session_id=session_id,
                    chat_history_number=chat_number,
                    user_request=user_request,
                    system_response=system_response,
                    query=query,
                    interest_preference=interest_json,
                    logistical_preference=logistical_json,
                )
            )

        return tables

    def to_history(
        self,
        tables: list[RecommendationSessionMemoryTable],
    ) -> RecommendationSessionHistory:
        """Convert multiple RecommendationSessionMemoryTable rows to RecommendationSessionHistory."""
        if not tables:
            return RecommendationSessionHistory()
        
        sorted_tables = sorted(tables, key=lambda t: t.chat_history_number)

        query_by_chat_number: dict[int, str] = {}
        user_request_by_chat_number: dict[int, str] = {}
        system_response_by_chat_number: dict[int, str] = {}
        interest_by_chat_number: dict[int, UserInterestPreferences] = {}
        logistical_by_chat_number: dict[int, UserLogisticalPreferences] = {}

        for table in sorted_tables:
            chat_number = table.chat_history_number

            if table.query:
                query_by_chat_number[chat_number] = table.query

            if table.user_request:
                user_request_by_chat_number[chat_number] = table.user_request
            if table.system_response:
                system_response_by_chat_number[chat_number] = table.system_response

            if table.interest_preference and table.interest_preference != "{}":
                try:
                    interest = UserInterestPreferences.model_validate_json(table.interest_preference)
                    interest_by_chat_number[chat_number] = interest
                except Exception as e:
                    logger.log(
                        VERBOSE,
                        "Failed to parse interest preference for user_id=%s session_id=%s: %s",
                        table.user_id,
                        table.session_id,
                        e,
                    )

            if table.logistical_preference and table.logistical_preference != "{}":
                try:
                    logistical = UserLogisticalPreferences.model_validate_json(table.logistical_preference)
                    logistical_by_chat_number[chat_number] = logistical
                except Exception as e:
                    logger.log(
                        VERBOSE,
                        "Failed to parse logistical preference for user_id=%s session_id=%s: %s",
                        table.user_id,
                        table.session_id,
                        e,
                    )

        return RecommendationSessionHistory(
            query_by_chat_number=query_by_chat_number,
            user_request_by_chat_number=user_request_by_chat_number,
            system_response_by_chat_number=system_response_by_chat_number,
            user_interest_preferences_by_chat_number=interest_by_chat_number,
            user_logistical_preferences_by_chat_number=logistical_by_chat_number,
        )
