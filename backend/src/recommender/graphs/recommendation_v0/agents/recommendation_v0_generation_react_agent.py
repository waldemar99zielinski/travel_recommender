from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import BasePromptTemplate

from recommender.graphs.recommendation_v0.agents.recommendation_v0_generation_models import AgentOutput
from recommender.graphs.recommendation_v0.agents.recommendation_v0_generation_react_prompt import (
    DATA,
    prompt,
)
from storage.models.chat_record import ChatRecord
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def _format_history(history: Sequence[ChatRecord] | None) -> str:
    if not history:
        return "None"

    parts: list[str] = []
    for row in history:
        parts.append(
            "User: "
            f"{row.user_request.strip() or 'None'}\n"
            "Assistant: "
            f"{row.system_response.strip() or 'None'}\n"
            "Query: "
            f"{row.synthesized_query.strip() or 'None'}"
        )
    return "\n\n".join(parts)


def _format_region_ids(region_ids: Sequence[str] | None) -> str:
    if not region_ids:
        return "None"
    return ", ".join(region_ids)


class RecommendationV0ReActGenerationAgent:
    """Prompt-only recommendation agent with structured output."""

    def __init__(
        self,
        *,
        llm: BaseChatModel,
        prompt_template: BasePromptTemplate = prompt,
    ) -> None:
        """Initialize the agent.

        Args:
            llm: Chat model used by the agent.
            prompt_template: Prompt template that receives runtime user inputs.
        """
        self._llm = llm
        self._prompt_template = prompt_template
        self._structured_output_llm = self._llm.with_structured_output(AgentOutput)

    def _build_prompt_inputs(
        self,
        *,
        user_input: str,
        included_region_ids: Sequence[str] | None,
        excluded_region_ids: Sequence[str] | None,
        history: Sequence[ChatRecord] | None,
    ) -> dict[str, str]:
        return {
            "user_message": user_input,
            "chat_history": _format_history(history),
            "included_region_ids": _format_region_ids(included_region_ids),
            "excluded_region_ids": _format_region_ids(excluded_region_ids),
            "travel_catalog_data": DATA,
        }

    def invoke(
        self,
        *,
        user_input: str,
        included_region_ids: Sequence[str] | None = None,
        excluded_region_ids: Sequence[str] | None = None,
        history: Sequence[ChatRecord] | None = None,
    ) -> AgentOutput:
        """Run the recommendation agent and return a structured response."""

        prompt_inputs = self._build_prompt_inputs(
            user_input=user_input,
            included_region_ids=included_region_ids,
            excluded_region_ids=excluded_region_ids,
            history=history,
        )
        prompt_value = self._prompt_template.format_prompt(**prompt_inputs)
        prompt_messages = prompt_value.to_messages()
        logger.verbose("RecommendationV0 prompt contains embedded catalog data and %d messages", len(prompt_messages))

        result = self._structured_output_llm.invoke(prompt_messages)
        logger.verbose("Raw structured LLM result: %s", result)

        output = AgentOutput.model_validate(result)
        logger.verbose(
            "RecommendationV0ReActGenerationAgent produced %d recommendations",
            len(output.recommendations),
        )
        return output
