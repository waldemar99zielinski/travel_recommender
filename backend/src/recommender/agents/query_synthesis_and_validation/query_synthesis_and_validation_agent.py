from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field

from recommender.agents.base.base_agent import BaseAgent
from recommender.agents.base.base_agent import BaseAgentBuilder
from recommender.agents.query_synthesis.recommendation_query_synthesis_agent import (
    RecommendationQuerySynthesisAgent,
)
from recommender.agents.query_synthesis.recommendation_query_synthesis_agent import (
    RecommendationQuerySynthesisInput,
)
from recommender.agents.query_synthesis_and_validation.query_synthesis_and_validation_prompt import (
    query_synthesis_and_validation_prompt_template,
)
from recommender.graphs.recommendation_v3.models import QuerySynthesisRoutingOutcome
from recommender.models.llm.llm import create_llm_chat_model
from recommender.models.llm.llm_config import LLMConfig
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class RecommendationQuerySynthesisAndValidationInput(BaseModel):
    """Input payload for recommendation_v3 query synthesis and validation."""

    current_user_input: str = Field(..., description="Raw user input for the current turn")
    previous_synthesized_query: str | None = Field(
        None,
        description="Previously accepted synthesized query",
    )
    chat_history: str = Field(
        ...,
        description="Conversation history with user messages and system replies",
    )


class RecommendationQuerySynthesisAndValidationResult(BaseModel):
    """Structured output for recommendation_v3 routing."""

    route: QuerySynthesisRoutingOutcome = Field(..., description="Selected route for the current turn")
    synthesized_query: str | None = Field(
        None,
        description="Conversation-aware synthesized query when relevant",
    )
    reason: str = Field(..., description="Short explanation of the chosen route")


class RecommendationQuerySynthesisAndValidationAgentBuilder(BaseAgentBuilder):
    """Builder for RecommendationQuerySynthesisAndValidationAgent."""

    def __init__(self) -> None:
        super().__init__(RecommendationQuerySynthesisAndValidationAgent)

    def build(self) -> "RecommendationQuerySynthesisAndValidationAgent":
        llm = self._llm or create_llm_chat_model(LLMConfig())
        prompt = self._prompt or query_synthesis_and_validation_prompt_template
        output_type = self._output_type or RecommendationQuerySynthesisAndValidationResult

        return RecommendationQuerySynthesisAndValidationAgent(
            llm=llm,
            prompt=prompt,
            output_type=output_type,
        )


class RecommendationQuerySynthesisAndValidationAgent(BaseAgent):
    """Synthesize a conversation-aware query and validate whether a new recommendation run is needed."""

    @staticmethod
    def _fallback_synthesized_query(inputs: RecommendationQuerySynthesisAndValidationInput) -> str:
        return RecommendationQuerySynthesisAgent._fallback_synthesized_query(
            RecommendationQuerySynthesisInput(
                current_user_request=inputs.current_user_input,
                previous_synthesized_query=inputs.previous_synthesized_query,
            )
        )

    def invoke(
        self,
        input: RecommendationQuerySynthesisAndValidationInput,
    ) -> RecommendationQuerySynthesisAndValidationResult:
        prompt_inputs = self.prompt.format_messages(
            current_user_input=input.current_user_input,
            previous_synthesized_query=input.previous_synthesized_query or "",
            chat_history=input.chat_history,
        )
        result = super().invoke(prompt_inputs)

        synthesized_query = (result.synthesized_query or "").strip() or None
        previous_query = (input.previous_synthesized_query or "").strip() or None

        if result.route == QuerySynthesisRoutingOutcome.RUN_NEW_RECOMMENDATION and synthesized_query is None:
            synthesized_query = self._fallback_synthesized_query(input)
            logger.warning(
                "RecommendationQuerySynthesisAndValidationAgent returned no synthesized_query for run_new_recommendation; using fallback query"
            )

        if result.route == QuerySynthesisRoutingOutcome.NOT_ENOUGH_INFORMATION_PROVIDED and synthesized_query is None:
            synthesized_query = previous_query or self._fallback_synthesized_query(input)

        if result.route == QuerySynthesisRoutingOutcome.OUTSIDE_OF_RECOMMENDER_SCOPE:
            synthesized_query = None

        return RecommendationQuerySynthesisAndValidationResult(
            route=result.route,
            synthesized_query=synthesized_query,
            reason=result.reason.strip(),
        )

    @classmethod
    def builder(cls) -> RecommendationQuerySynthesisAndValidationAgentBuilder:
        return RecommendationQuerySynthesisAndValidationAgentBuilder()
