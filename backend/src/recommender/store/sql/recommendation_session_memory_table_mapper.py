from __future__ import annotations

from recommender.models.data_flow.recommendation_session_history import RecommendationSessionHistory
from recommender.models.data_flow.user_preferences import UserInterestPreferences
from recommender.models.data_flow.user_preferences import UserLogisticalPreferences
from recommender.store.sql.tables.recommendation_session_memory_table import (
    RecommendationSessionMemoryTable,
)
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

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
        
        query_history = history.query_history or []
        chat_history = history.chat_history or []
        interest_history = history.user_interest_preferences_history or []
        logistical_history = history.user_logistical_preferences_history or []
        
        max_len = max(
            len(query_history),
            len(chat_history) // 2,
            len(interest_history),
            len(logistical_history),
        )
        
        for i in range(max_len):
            user_request = chat_history[i * 2] if i * 2 < len(chat_history) else ""
            system_response = chat_history[i * 2 + 1] if i * 2 + 1 < len(chat_history) else ""
            query = query_history[i] if i < len(query_history) else ""
            interest_pref = interest_history[i] if i < len(interest_history) else None
            logistical_pref = logistical_history[i] if i < len(logistical_history) else None
            
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
                    chat_history_number=i,
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
        
        query_history: list[str] = []
        chat_history: list[str] = []
        interest_history: list[UserInterestPreferences] = []
        logistical_history: list[UserLogisticalPreferences] = []
        
        for table in sorted_tables:
            query_history.append(table.query)
            
            if table.user_request:
                chat_history.append(table.user_request)
            if table.system_response:
                chat_history.append(table.system_response)
            
            if table.interest_preference and table.interest_preference != "{}":
                try:
                    interest = UserInterestPreferences.model_validate_json(table.interest_preference)
                    interest_history.append(interest)
                except Exception as e:
                    logger.verbose(f"Failed to parse interest preference for table with user_id {table.user_id} and session_id {table.session_id}: {e}")
            
            if table.logistical_preference and table.logistical_preference != "{}":
                try:
                    logistical = UserLogisticalPreferences.model_validate_json(table.logistical_preference)
                    logistical_history.append(logistical)
                except Exception as e:
                    logger.verbose(f"Failed to parse logistical preference for table with user_id {table.user_id} and session_id {table.session_id}: {e}")
        
        return RecommendationSessionHistory(
            query_history=query_history,
            chat_history=chat_history,
            user_interest_preferences_history=interest_history,
            user_logistical_preferences_history=logistical_history,
        )
