from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.prompts import BasePromptTemplate
from langchain_core.runnables import Runnable
from pydantic import ValidationError
from sqlalchemy.engine import Engine

from recommender.graphs.recommendation_v1.agents.recommendation_v1_generation_models import AgentOutput
from recommender.graphs.recommendation_v1.agents.recommendation_v1_generation_react_prompt import (
    prompt,
)
from recommender.tools import create_travel_destination_sql_query_tool
from storage.models.chat_record import ChatRecord
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

_STRUCTURED_OUTPUT_FALLBACK_PROMPT = """
Convert the completed recommendation agent transcript into the AgentOutput schema.

Requirements:
- `system_response` must be a concise final user-facing answer grounded in the transcript.
- `recommendations` must only contain `region_id` and `explanation` values supported by the transcript.
- Return an empty recommendations list when no recommendation should be made.

Transcript:
{transcript}
""".strip()


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


def _serialize_messages(messages: Sequence[BaseMessage]) -> str:
    parts: list[str] = []

    for message in messages:
        role = getattr(message, "type", message.__class__.__name__)
        content = getattr(message, "content", "")
        parts.append(f"{role}: {content}")

        tool_calls = getattr(message, "tool_calls", None)
        if tool_calls:
            parts.append(f"tool_calls: {tool_calls}")

    return "\n\n".join(parts)


class RecommendationV1ReActGenerationAgent:
    """ReAct recommendation agent with prompt injection and structured output."""

    def __init__(
        self,
        *,
        llm: BaseChatModel,
        db_engine: Engine,
        prompt_template: BasePromptTemplate = prompt,
    ) -> None:
        """Initialize the agent.

        Args:
            llm: Chat model used by the agent.
            db_engine: Database engine used by the SQL execution tool.
            prompt_template: Prompt template that receives runtime user inputs.
        """
        self._llm = llm
        self._prompt_template = prompt_template
        self._structured_output_llm = self._llm.with_structured_output(AgentOutput)
        self._agent: Runnable = create_agent(
            model=self._llm,
            tools=[create_travel_destination_sql_query_tool(db_engine)],
            response_format=AgentOutput,
            # debug=True,
        )

    def _log_agent_result(self, result: Any) -> None:
        logger.verbose("Raw agent result: %s", result)

        if not isinstance(result, dict):
            return

        structured_response = result.get("structured_response")
        if structured_response is not None:
            logger.verbose("Agent structured response: %s", structured_response)
    

        messages = result.get("messages")
        if isinstance(messages, Sequence):
            logger.verbose("Agent message transcript:\n%s", _serialize_messages(messages))

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

    def _extract_output_from_messages(self, messages: Sequence[BaseMessage]) -> AgentOutput:
        last_message = messages[-1] if messages else None
        last_message_content = getattr(last_message, "content", None)

        if isinstance(last_message_content, str) and last_message_content.strip():
            try:
                return AgentOutput.model_validate_json(last_message_content)
            except ValidationError:
                logger.warning(
                    "RecommendationV1ReActGenerationAgent could not parse final message as AgentOutput JSON; using fallback structured-output pass"
                )

        fallback_prompt = _STRUCTURED_OUTPUT_FALLBACK_PROMPT.format(
            transcript=_serialize_messages(messages),
        )
        fallback_result = self._structured_output_llm.invoke(fallback_prompt)
        return AgentOutput.model_validate(fallback_result)

    def _extract_output(self, result: Any) -> AgentOutput:
        if isinstance(result, dict):
            structured_response = result.get("structured_response")
            if structured_response is not None:
                return AgentOutput.model_validate(structured_response)

            messages = result.get("messages")
            if isinstance(messages, Sequence):
                logger.warning(
                    "RecommendationV1ReActGenerationAgent result did not include structured_response; deriving AgentOutput from returned messages"
                )
                return self._extract_output_from_messages(messages)

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
        prompt_messages = prompt_value.to_messages()

        result = self._agent.invoke({"messages": prompt_messages})
        self._log_agent_result(result)

        output = self._extract_output(result)
        logger.verbose(
            "RecommendationV1ReActGenerationAgent produced %d recommendations",
            len(output.recommendations),
        )
        return output
