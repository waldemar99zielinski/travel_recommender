from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

from recommender.models.data_flow.user_preferences import UserInterestPreferences, UserLogisticalPreferences
from recommender.models.data_flow.recommendation_output import RecommendationBase
from recommender.models.data_flow.recommendation_response import RecommendationResponse

class RecommendationStatusEnum(str, Enum):
    """Status of the recommendation process, used for routing and response handling."""

    IN_PROGRESS = "in_progress"

    SUCCESS = "success"

    NO_PREFERENCES = "no_preferences"
    ERROR = "error"

class RecommendationGraphState(BaseModel):
    user_input: str = Field(..., description="Raw user query input")
    status: RecommendationStatusEnum = Field(
        RecommendationStatusEnum.IN_PROGRESS,
        description="Current status of the recommendation process"
    )
    extracted_user_interests_preferences: Optional[UserInterestPreferences] = Field(
        None,
        description="Extracted user interest preferences"
    )
    extracted_user_logistical_preferences: Optional[UserLogisticalPreferences] = Field(
        None,
        description="Extracted user logistical preferences"
    )
    recommendation: Optional[list[RecommendationBase]] = Field(
        None,
        description="Ranked recommendations returned from vector search"
    )
    response: Optional[RecommendationResponse] = Field(
        None,
        description="Final response payload shared across graph branches"
    )

    def __repr__(self) -> str:
        lines: list[str] = ["RecommendationGraphState("]
        lines.append(f"  user_input={self.user_input!r},")
        lines.append(f"  status={self.status.value!r},")

        if self.extracted_user_interests_preferences is None:
            lines.append("  extracted_user_interests_preferences=None,")
        else:
            preferences_repr = repr(self.extracted_user_interests_preferences).replace("\n", "\n  ")
            lines.append(f"  extracted_user_interests_preferences={preferences_repr},")

        if self.extracted_user_logistical_preferences is None:
            lines.append("  extracted_user_logistical_preferences=None,")
        else:
            logistical_preferences_repr = repr(self.extracted_user_logistical_preferences).replace("\n", "\n  ")
            lines.append(
                "  extracted_user_logistical_preferences="
                f"{logistical_preferences_repr},"
            )

        recommendation_count = len(self.recommendation) if self.recommendation else 0
        lines.append(f"  recommendation_count={recommendation_count},")
        if self.recommendation:
            top_recommendation = self.recommendation[0]
            lines.append(
                "  top_recommendation="
                f"{{region={top_recommendation.region!r}, score={top_recommendation.score:.4f}}},"
            )

        if self.response is None:
            lines.append("  response=None,")
        else:
            lines.append(
                "  response="
                f"{{message={self.response.message!r}, "
                f"recommendations={len(self.response.recommendations)}}},"
            )

        lines.append(")")
        return "\n".join(lines)
