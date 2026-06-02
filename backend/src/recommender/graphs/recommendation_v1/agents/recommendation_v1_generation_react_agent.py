from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import BasePromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool

from recommender.graphs.recommendation_v1.agents.recommendation_v1_generation_models import AgentOutput
from recommender.graphs.recommendation_v1.agents.recommendation_v1_generation_react_prompt import (
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


class RecommendationV1ReActGenerationAgent:
    """ReAct recommendation agent with prompt injection and structured output."""

    def __init__(
        self,
        *,
        llm: BaseChatModel,
        tools: Sequence[BaseTool],
        prompt_template: BasePromptTemplate = prompt,
    ) -> None:
        """Initialize the agent.

        Args:
            llm: Chat model used by the agent.
            tools: Tools available to the agent during tool-calling.
            prompt_template: Prompt template that receives runtime user inputs.
        """
        self._llm = llm
        self._tools = list(tools)
        self._prompt_template = prompt_template
        self._agent: Runnable = create_agent(
            model=self._llm,
            tools=self._tools,
            response_format=AgentOutput,
        )

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
        }

    def _extract_output(self, result: Any) -> AgentOutput:
        if isinstance(result, dict) and "structured_response" in result:
            return AgentOutput.model_validate(result["structured_response"])
        return AgentOutput.model_validate(result)

    def invoke(
        self,
        *,
        user_input: str,
        included_region_ids: Sequence[str] | None = None,
        excluded_region_ids: Sequence[str] | None = None,
        history: Sequence[ChatRecord] | None = None,
    ) -> AgentOutput:
        """Run the recommendation agent and return a structured response.

        Args:
            user_input: Current user request.
            included_region_ids: Region IDs that should be preferred.
            excluded_region_ids: Region IDs that should be avoided.
            history: Persisted chat history for the current session.

        Returns:
            AgentOutput: Structured conversational answer and recommendations.
        """
        prompt_inputs = self._build_prompt_inputs(
            user_input=user_input,
            included_region_ids=included_region_ids,
            excluded_region_ids=excluded_region_ids,
            history=history,
        )
        prompt_value = self._prompt_template.format_prompt(**prompt_inputs)
        result = self._agent.invoke({"messages": prompt_value.to_messages()})

        output = self._extract_output(result)
        logger.verbose(
            "RecommendationV1ReActGenerationAgent produced %d recommendations",
            len(output.recommendations),
        )
        return output
