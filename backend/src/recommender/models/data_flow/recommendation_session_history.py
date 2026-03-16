from __future__ import annotations

from typing import Mapping

from pydantic import BaseModel
from pydantic import Field

from recommender.models.data_flow.user_preferences import UserInterestPreferences
from recommender.models.data_flow.user_preferences import UserLogisticalPreferences


def _sorted_chat_numbers(values: Mapping[int, object]) -> list[int]:
    return sorted(values.keys())


def _latest_chat_number(values: Mapping[int, object]) -> int | None:
    if not values:
        return None
    return max(values)

class RecommendationSessionHistory(BaseModel):
    """Data model for storing recommendation session history in SQL store."""

    query_by_chat_number: dict[int, str] = Field(
        default_factory=dict,
        description="Mapping from chat history number to synthesized query for that turn",
    )
    user_request_by_chat_number: dict[int, str] = Field(
        default_factory=dict,
        description="Mapping from chat history number to user request for that turn",
    )
    system_response_by_chat_number: dict[int, str] = Field(
        default_factory=dict,
        description="Mapping from chat history number to system response for that turn",
    )
    user_interest_preferences_by_chat_number: dict[int, UserInterestPreferences] = Field(
        default_factory=dict,
        description="Mapping from chat history number to extracted interest preferences for that turn",
    )
    user_logistical_preferences_by_chat_number: dict[int, UserLogisticalPreferences] = Field(
        default_factory=dict,
        description="Mapping from chat history number to extracted logistical preferences for that turn",
    )

    def next_chat_history_number(self) -> int:
        """Return next chat history number for appending a new turn."""
        all_numbers: set[int] = set(self.query_by_chat_number)
        all_numbers.update(self.user_request_by_chat_number)
        all_numbers.update(self.system_response_by_chat_number)
        all_numbers.update(self.user_interest_preferences_by_chat_number)
        all_numbers.update(self.user_logistical_preferences_by_chat_number)
        if not all_numbers:
            return 0
        return max(all_numbers) + 1

    def query_history_list(self) -> list[str]:
        """Return query history ordered by chat history number."""
        return [
            self.query_by_chat_number[chat_number]
            for chat_number in _sorted_chat_numbers(self.query_by_chat_number)
        ]

    def latest_query_chat_number(self) -> int | None:
        """Return latest chat number with a synthesized query, if present."""
        return _latest_chat_number(self.query_by_chat_number)

    def latest_query(self) -> str | None:
        """Return latest synthesized query, if present."""
        latest_chat_number = self.latest_query_chat_number()
        if latest_chat_number is None:
            return None
        return self.query_by_chat_number.get(latest_chat_number)

    def chat_history_list(self) -> list[str]:
        """Return alternating user and system chat history ordered by chat history number."""
        all_numbers: set[int] = set(self.user_request_by_chat_number)
        all_numbers.update(self.system_response_by_chat_number)
        chat_history: list[str] = []

        for chat_number in sorted(all_numbers):
            user_request = self.user_request_by_chat_number.get(chat_number)
            if user_request:
                chat_history.append(user_request)
            system_response = self.system_response_by_chat_number.get(chat_number)
            if system_response:
                chat_history.append(system_response)

        return chat_history

    def user_interest_preferences_history_list(self) -> list[UserInterestPreferences]:
        """Return interest preferences ordered by chat history number."""
        return [
            self.user_interest_preferences_by_chat_number[chat_number]
            for chat_number in _sorted_chat_numbers(self.user_interest_preferences_by_chat_number)
        ]

    def user_logistical_preferences_history_list(self) -> list[UserLogisticalPreferences]:
        """Return logistical preferences ordered by chat history number."""
        return [
            self.user_logistical_preferences_by_chat_number[chat_number]
            for chat_number in _sorted_chat_numbers(self.user_logistical_preferences_by_chat_number)
        ]
