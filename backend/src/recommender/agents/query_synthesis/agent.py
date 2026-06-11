from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field

from recommender.agents.base.base_agent import BaseAgent
from recommender.agents.base.base_agent import BaseAgentBuilder
from recommender.agents.query_synthesis.prompt import (
    prompt,
)
from recommender.models.llm.llm import create_llm_chat_model
from recommender.models.llm.llm_config import LLMConfig
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class QuerySynthesisInput(BaseModel):
    """Input payload for interest-focused recommendation query synthesis."""

    current_user_request: str = Field(
        ...,
        description="Raw user request from the current chat turn",
    )
    previous_synthesized_query: str | None = Field(
        None,
        description="Synthesized cumulative query from the previous turn",
    )


class QuerySynthesisResult(BaseModel):
    """Structured output containing cumulative interest-focused synthesized query."""

    synthesized_query: str = Field(
        ...,
        description="Updated cumulative synthesized query for this turn",
    )


class QuerySynthesisAgentBuilder(BaseAgentBuilder):
    """Builder for QuerySynthesisAgent."""

    def __init__(self) -> None:
        super().__init__(QuerySynthesisAgent)

    def build(self) -> "QuerySynthesisAgent":
        llm = self._llm or create_llm_chat_model(LLMConfig())
        prompt_template = self._prompt or prompt
        output_type = self._output_type or QuerySynthesisResult

        return QuerySynthesisAgent(
            llm=llm,
            prompt=prompt_template,
            output_type=output_type,
        )


class QuerySynthesisAgent(BaseAgent):
    """Agent that synthesizes a cumulative interest-focused recommendation query."""

    @staticmethod
    def _fallback_synthesized_query(inputs: QuerySynthesisInput) -> str:
        previous_synthesized_query = (inputs.previous_synthesized_query or "").strip()
        current_user_request = inputs.current_user_request.strip()

        if previous_synthesized_query and current_user_request:
            return f"{previous_synthesized_query} {current_user_request}"
        if current_user_request:
            return current_user_request
        if previous_synthesized_query:
            return previous_synthesized_query

        raise ValueError(
            "QuerySynthesisAgent cannot build a synthesized query from empty inputs"
        )

    def invoke(
        self,
        inputs: QuerySynthesisInput,
    ) -> QuerySynthesisResult:
        prompt_inputs = self.prompt.format_messages(
            current_user_request=inputs.current_user_request,
            previous_synthesized_query=inputs.previous_synthesized_query or "",
        )
        result = super().invoke(prompt_inputs)

        synthesized_query = result.synthesized_query.strip()
        if not synthesized_query:
            synthesized_query = self._fallback_synthesized_query(inputs)
            logger.warning(
                "QuerySynthesisAgent returned an empty synthesized_query; using fallback query"
            )
        return QuerySynthesisResult(synthesized_query=synthesized_query)

    @classmethod
    def builder(cls) -> QuerySynthesisAgentBuilder:
        return QuerySynthesisAgentBuilder()
