from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field

from recommender.models.data_flow.user_preferences import UserInterestPreferences, UserLogisticalPreferences

class RecommendationSessionHistory(BaseModel):
    """Data model for storing recommendation session history in SQL store."""

    query_history: list[str] = Field(
        default_factory=list,
        description="List of all extracted queries in the session history",
    )
    chat_history: list[str] = Field(
        default_factory=list,
        description="List of alternating user requests and system responses in the session history",
    )
    user_interest_preferences_history: list[UserInterestPreferences] = Field(
        default_factory=list,
        description="List of extracted user interest preferences at each turn in the session history",
    )
    user_logistical_preferences_history: list[UserLogisticalPreferences] = Field(
        default_factory=list,
        description="List of extracted user logistical preferences at each turn in the session history",
    )