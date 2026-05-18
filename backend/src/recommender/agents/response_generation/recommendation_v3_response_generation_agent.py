from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field

from recommender.agents.base.base_agent import BaseAgent
from recommender.agents.base.base_agent import BaseAgentBuilder
from recommender.agents.response_generation.recommendation_v3_response_generation_prompt import (
    recommendation_v3_response_generation_prompt_template,
)
from recommender.graphs.recommendation_v3.models import QuerySynthesisRoutingOutcome
from recommender.models.llm.llm import create_llm_chat_model
from recommender.models.llm.llm_config import LLMConfig
from storage.models.travel_destination import TravelDestinationRecord


class RecommendationV3ResponseGenerationInput(BaseModel):
    """Input payload for recommendation_v3 response generation."""

    user_input: str = Field(..., description="Raw user input from the current turn")
    outcome: QuerySynthesisRoutingOutcome = Field(
        ...,
        description="Routing outcome that determines the response strategy",
    )
    reason: str = Field(
        ...,
        description="Short explanation of why the outcome was chosen",
    )
    synthesized_query: str | None = Field(
        None,
        description="Search query used for the recommendation run",
    )
    top_k_recommendations: list[TravelDestinationRecord] = Field(
        default_factory=list,
        description="Top-k travel destinations with metadata and descriptions",
    )


class RecommendationV3ResponseGenerationResult(BaseModel):
    """Final response message from the recommendation_v3 response generation agent."""

    message: str = Field(..., description="Generated conversational response for the user")


class RecommendationV3ResponseGenerationAgentBuilder(BaseAgentBuilder):
    """Builder for RecommendationV3ResponseGenerationAgent."""

    def __init__(self) -> None:
        super().__init__(RecommendationV3ResponseGenerationAgent)

    def build(self) -> RecommendationV3ResponseGenerationAgent:
        llm = self._llm or create_llm_chat_model(LLMConfig())
        prompt = self._prompt or recommendation_v3_response_generation_prompt_template
        output_type = self._output_type or RecommendationV3ResponseGenerationResult

        return RecommendationV3ResponseGenerationAgent(
            llm=llm,
            prompt=prompt,
            output_type=output_type,
        )


class RecommendationV3ResponseGenerationAgent(BaseAgent):
    """Generate a conversational response based on the recommendation_v3 routing outcome.

    Handles three outcomes:
    - RUN_NEW_RECOMMENDATION: references top-k destinations with descriptions justifying the match.
    - OUTSIDE_OF_RECOMMENDER_SCOPE: politely explains scope boundaries.
    - NOT_ENOUGH_INFORMATION_PROVIDED: asks for missing details or answers a general query.
    """

    def invoke(
        self,
        inputs: RecommendationV3ResponseGenerationInput,
    ) -> RecommendationV3ResponseGenerationResult:
        prompt_inputs = self.prompt.format_messages(
            user_input=inputs.user_input,
            outcome=inputs.outcome.value,
            reason=inputs.reason,
            synthesized_query=inputs.synthesized_query or "",
            top_k_recommendations_summary=self._summarize_recommendations(inputs.top_k_recommendations),
        )
        return super().invoke(prompt_inputs)

    @staticmethod
    def _summarize_recommendations(recommendations: list[TravelDestinationRecord]) -> str:
        if not recommendations:
            return "None"

        parts: list[str] = []
        for item in recommendations:
            parts.append(
                f"name={item.region} "
                f"(id={item.id}), "
                f"cost_per_week={item.cost_per_week}, "
                f"popularity={item.popularity}, "
                f"description={item.description}"
            )
        return "\n".join(parts)

    @classmethod
    def builder(cls) -> RecommendationV3ResponseGenerationAgentBuilder:
        return RecommendationV3ResponseGenerationAgentBuilder()
