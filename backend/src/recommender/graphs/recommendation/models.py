from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

from recommender.models.data_flow.user_preferences import UserInterestPreferences, UserLogisticalPreferences
from recommender.models.data_flow.recommendation_output import Recommendation
from recommender.models.data_flow.recommendation_message_output import RecommendationMessageOutput
from recommender.models.data_flow.recommendation_session_history import RecommendationSessionHistory
from recommender.models.session.session import Session

class RecommendationStatusEnum(str, Enum):
    """Status of the recommendation process, used for routing and response handling."""

    IN_PROGRESS = "in_progress"
    RECOMMENDATION_GENERATED = "recommendation_generated"

    NO_PREFERENCES = "no_preferences"
    SUCCESS = "success"
    ERROR = "error"

class RecommendationGraphState(BaseModel):
    session: Session = Field(..., description="Conversation scope identifiers")
    user_input: str = Field(..., description="Raw user query input")
    query: Optional[str] = Field(
        None,
        description="Synthesized query built from recent user input and session history",
    )
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
    recommendation: Optional[list[Recommendation]] = Field(
        None,
        description="Ranked recommendations returned from vector search"
    )
    response: Optional[RecommendationMessageOutput] = Field(
        None,
        description="Final response payload shared across graph branches"
    )
    history: Optional[RecommendationSessionHistory] = Field(
        None,
        description="Full session history for context and debugging purposes"
    )

    def __repr__(self) -> str:
        lines: list[str] = ["RecommendationGraphState("]
        session_repr = repr(self.session).replace("\n", "\n  ")
        lines.append(f"  session={session_repr},")
        lines.append(f"  user_input={self.user_input!r},")
        lines.append(f"  query={self.query!r},")
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
            interest_score_repr = (
                f"{top_recommendation.interest_score:.4f}"
                if top_recommendation.interest_score is not None
                else "None"
            )
            logistical_score_repr = (
                f"{top_recommendation.logistical_score:.4f}"
                if top_recommendation.logistical_score is not None
                else "None"
            )
            lines.append(
                "  top_recommendation="
                f"{{region={top_recommendation.region!r}, interest_score={interest_score_repr}, "
                f"logistical_score={logistical_score_repr}, ranking_score={top_recommendation.ranking_score!r}}},"
            )

        if self.response is None:
            lines.append("  response=None,")
        else:
            lines.append(
                "  response="
                f"{{message={self.response.message!r}}}"
            )

        lines.append(f"  history={self.history!r},")

        lines.append(")")
        return "\n".join(lines)
