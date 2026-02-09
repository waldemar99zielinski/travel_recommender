from typing import TypedDict
from recommender.models.data_flow.user_preferences import UserPreferences
from recommender.models.data_flow.recommendation_output import RecommendationOutput

class RecommendationGraphState(TypedDict):
    user_input: str
    extracted_preferences: UserPreferences
    recommendation: RecommendationOutput

