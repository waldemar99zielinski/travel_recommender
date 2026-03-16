from __future__ import annotations

from typing import cast

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from pydantic import Field

from recommender.agents.base.base_agent import BaseAgent
from recommender.agents.base.base_agent import BaseAgentBuilder
from recommender.agents.query_synthesis.recommendation_query_synthesis_prompt import (
    recommendation_query_synthesis_prompt_template,
)
from recommender.models.llm.llm import create_llm_chat_model
from recommender.models.llm.llm_config import LLMConfig


class RecommendationQuerySynthesisInput(BaseModel):
    """Input payload for recommendation query synthesis."""

    current_user_request: str = Field(
        ...,
        description="Raw user request from the current chat turn",
    )
    previous_synthesized_query: str | None = Field(
        None,
        description="Synthesized cumulative query from the previous turn",
    )


class RecommendationQuerySynthesisResult(BaseModel):
    """Structured output containing cumulative synthesized query."""

    synthesized_query: str = Field(
        ...,
        description="Updated cumulative synthesized query for this turn",
    )


class RecommendationQuerySynthesisAgentBuilder(BaseAgentBuilder):
    """Builder for RecommendationQuerySynthesisAgent."""

    def __init__(self) -> None:
        super().__init__(RecommendationQuerySynthesisAgent)

    def build(self) -> "RecommendationQuerySynthesisAgent":
        llm = self._llm or create_llm_chat_model(LLMConfig())
        prompt = self._prompt or recommendation_query_synthesis_prompt_template
        output_type = self._output_type or RecommendationQuerySynthesisResult

        return RecommendationQuerySynthesisAgent(
            llm=llm,
            prompt=prompt,
            output_type=output_type,
        )


class RecommendationQuerySynthesisAgent(BaseAgent):
    """Agent that synthesizes cumulative recommendation query from chat turns."""

    def invoke(
        self,
        inputs: RecommendationQuerySynthesisInput,
    ) -> RecommendationQuerySynthesisResult:
        prompt_inputs = self.prompt.format_messages(
            current_user_request=inputs.current_user_request,
            previous_synthesized_query=inputs.previous_synthesized_query or "",
        )
        result = super().invoke(prompt_inputs)

        synthesized_query = result.synthesized_query.strip()
        if not synthesized_query:
            raise ValueError("RecommendationQuerySynthesisAgent returned an empty synthesized_query")
        return RecommendationQuerySynthesisResult(synthesized_query=synthesized_query)

    @classmethod
    def builder(cls) -> RecommendationQuerySynthesisAgentBuilder:
        return RecommendationQuerySynthesisAgentBuilder()
