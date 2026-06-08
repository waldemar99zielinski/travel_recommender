from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel
from pydantic import Field

from recommender.graphs.recommendation_v2.agents.query_synthesis.query_synthesis_prompt import (
    prompt,
)
from recommender.graphs.recommendation_v2.models import serialize_chat_history
from storage.models.chat_record import ChatRecord
class RecommendationV2SynthesizedUserRequestInput(BaseModel):
    """Input payload for recommendation_v2 synthesized user request generation."""

    current_user_request: str = Field(
        ...,
        description="Raw user request from the current chat turn",
    )
    previous_synthesized_query: str | None = Field(
        None,
        description="Synthesized cumulative query from the previous turn",
    )
    chat_history: list[ChatRecord] | None = Field(
        None,
        description="Persisted chat history for the active session",
    )


class RecommendationV2SynthesizedUserRequestResult(BaseModel):
    """Structured output containing the synthesized user request for this turn."""

    synthesized_query: str = Field(
        ...,
        description="General context of interest synthesized for the current turn",
    )
    keywords: list[str] = Field(
        default_factory=list,
        description="Concrete direct-search keywords extracted from the synthesized query",
    )


class RecommendationV2SynthesizedUserRequestAgent:
    """Agent that synthesizes the current user request with prior session context."""

    def __init__(
        self,
        *,
        llm: BaseChatModel,
    ) -> None:
        self._llm = llm
        self._llm.bind(
            temperature=0.1,
        )
        self._prompt_template = prompt
        self._structured_output_llm = self._llm.with_structured_output(
            RecommendationV2SynthesizedUserRequestResult,
        )

    def invoke(
        self,
        inputs: RecommendationV2SynthesizedUserRequestInput,
    ) -> RecommendationV2SynthesizedUserRequestResult:
        prompt_inputs = {
            "current_user_request": inputs.current_user_request,
            "previous_synthesized_query": inputs.previous_synthesized_query or "None",
            "chat_history": serialize_chat_history(inputs.chat_history),
        }
        
        prompt_value = self._prompt_template.format_prompt(**prompt_inputs)
        prompt_messages = prompt_value.to_messages()
        result = self._structured_output_llm.invoke(prompt_messages)
        return RecommendationV2SynthesizedUserRequestResult.model_validate(result)
