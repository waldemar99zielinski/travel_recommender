from typing import TypedDict
from recommender.models.data_flow.user_preferences import UserPreferences

class RecommendationGraphState(TypedDict):
    user_input: str
    extracted_preferences: UserPreferences
    recommendation: str

