from __future__ import annotations

from typing import Any
from typing import Sequence
from typing import cast

from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from recommender.agents.base.base_agent import BaseAgent
from recommender.agents.base.base_agent import BaseAgentBuilder
from recommender.agents.response_generation.recommendation_response_generation_prompt import (
    recommendation_response_generation_prompt_template,
)
from recommender.graphs.recommendation.models import RecommendationStatusEnum
from recommender.models.data_flow.recommendation_message_output import RecommendationMessageOutput
from recommender.models.data_flow.recommendation_output import Recommendation
from recommender.models.data_flow.user_preferences import UserInterestPreferences
from recommender.models.data_flow.user_preferences import UserLogisticalPreferences
from recommender.models.llm.llm import create_llm_chat_model
from recommender.models.llm.llm_config import LLMConfig

TOP_K_FOR_MESSAGE = 3


class RecommendationResponseGenerationResult(BaseModel):
    """Final response generation result with normalized final status."""

    message: str = Field(..., description="Generated response message to be shared with the user")


class RecommendationResponseGenerationInput(BaseModel):
    """Input payload for response generation from recommendation graph state."""

    user_input: str
    status: RecommendationStatusEnum
    interest_preferences: UserInterestPreferences | None = None
    logistical_preferences: UserLogisticalPreferences | None = None
    recommendations: list[Recommendation] = Field(default_factory=list)


class RecommendationResponseGenerationAgentBuilder(BaseAgentBuilder):
    """Builder for RecommendationResponseGenerationAgent."""

    def __init__(self) -> None:
        super().__init__(RecommendationResponseGenerationAgent)

    def build(self) -> "RecommendationResponseGenerationAgent":
        llm = self._llm or create_llm_chat_model(LLMConfig())
        prompt = self._prompt or recommendation_response_generation_prompt_template
        output_type = self._output_type or RecommendationMessageOutput

        return RecommendationResponseGenerationAgent(
            llm=llm,
            prompt=prompt,
            output_type=output_type,
        )


class RecommendationResponseGenerationAgent(BaseAgent):
    """Generate a short conversational message from recommendation graph state fields."""

    def invoke(
        self,
        input: RecommendationResponseGenerationInput,
    ) -> RecommendationResponseGenerationResult:
        prompt_inputs = self.prompt.format_messages(
            user_input=input.user_input,
            status=input.status.value,
            interest_preferences_summary=self._summarize_interest_preferences(input.interest_preferences),
            logistical_preferences_summary=self._summarize_logistical_preferences(input.logistical_preferences),
            recommendations_summary=self._summarize_recommendations(input.recommendations),
        )
        return super().invoke(prompt_inputs)

    @staticmethod
    def _summarize_interest_preferences(preferences: UserInterestPreferences | None) -> str:
        if preferences is None:
            return "None"

        parts: list[str] = []
        for field_name in UserInterestPreferences.model_fields:
            if field_name == "raw_user_query":
                continue
            value = getattr(preferences, field_name)
            if value is not None:
                parts.append(f"{field_name}: strength={value.strength}")

        return ", ".join(parts) if parts else "None"

    @staticmethod
    def _summarize_logistical_preferences(preferences: UserLogisticalPreferences | None) -> str:
        if preferences is None:
            return "None"

        parts: list[str] = []
        if preferences.price is not None:
            parts.append(
                "price="
                f"min:{preferences.price.min_cost_per_week}, "
                f"max:{preferences.price.max_cost_per_week}, "
                f"tier:{preferences.price.budget_tier}"
            )
        if preferences.popularity is not None:
            parts.append(f"popularity_strength={preferences.popularity.strength}")
        if preferences.time_of_year is not None:
            parts.append(
                "time_of_year="
                f"months:{preferences.time_of_year.months}, "
                f"season:{preferences.time_of_year.season}"
            )

        return "; ".join(parts) if parts else "None"

    @staticmethod
    def _summarize_recommendations(recommendations: list[Recommendation]) -> str:
        if not recommendations:
            return "None"

        names = [item.u_name for item in recommendations[:TOP_K_FOR_MESSAGE]]
        return (
            f"top_k={len(names)}; "
            f"total_results={len(recommendations)}; "
            f"top_results={', '.join(names)}"
        )

    @classmethod
    def builder(cls) -> RecommendationResponseGenerationAgentBuilder:
        return RecommendationResponseGenerationAgentBuilder()
