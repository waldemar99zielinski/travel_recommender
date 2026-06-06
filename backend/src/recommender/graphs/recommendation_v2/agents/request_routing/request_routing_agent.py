from __future__ import annotations

from typing import Literal

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel
from pydantic import Field

from recommender.graphs.recommendation_v2.agents.request_routing.request_routing_prompt import (
    prompt,
)
from recommender.graphs.recommendation_v2.models import serialize_chat_history
from storage.models.chat_record import ChatRecord
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class RecommendationV2RequestRoutingInput(BaseModel):
    """Input payload for recommendation_v2 request routing."""

    current_user_request: str = Field(
        ...,
        description="Raw user request from the current chat turn",
    )
    chat_history: list[ChatRecord] | None = Field(
        None,
        description="Persisted chat history for the active session",
    )


class RecommendationV2RequestRoutingResult(BaseModel):
    """Structured routing decision for the current recommendation_v2 turn."""

    decision: Literal[
        "out_of_system_scope",
        "new_recommendation_run",
        "need_more_information_from_user",
    ] = Field(
        ...,
        description="How the graph should handle the current user turn",
    )
    reason: str = Field(
        ...,
        description="Short explanation for the selected routing decision",
    )


class RecommendationV2RequestRoutingAgent:
    """Agent that routes the current user turn for recommendation_v2."""

    def __init__(
        self,
        *,
        llm: BaseChatModel,
    ) -> None:
        self._llm = llm
        self._prompt_template = prompt
        self._structured_output_llm = self._llm.with_structured_output(
            RecommendationV2RequestRoutingResult,
        )

    def invoke(
        self,
        inputs: RecommendationV2RequestRoutingInput,
    ) -> RecommendationV2RequestRoutingResult:
        prompt_inputs = {
            "current_user_request": inputs.current_user_request,
            "chat_history": serialize_chat_history(inputs.chat_history),
        }
        prompt_value = self._prompt_template.format_prompt(**prompt_inputs)
        prompt_messages = prompt_value.to_messages()
        result = self._structured_output_llm.invoke(prompt_messages)
        logger.verbose("Raw request-routing structured LLM result: %s", result)
        output = RecommendationV2RequestRoutingResult.model_validate(result)

        reason = output.reason.strip() or "No reason provided"
        return RecommendationV2RequestRoutingResult(
            decision=output.decision,
            reason=reason,
        )
