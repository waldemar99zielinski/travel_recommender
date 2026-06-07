from __future__ import annotations

from typing import Any

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel

from recommender.graphs.recommendation_v2.agents.recommendation_research.models import (
    RecommendationV2RecommendationResearchInput,
)
from recommender.graphs.recommendation_v2.agents.recommendation_research.models import (
    RecommendationV2RecommendationResearchResult,
)
from recommender.graphs.recommendation_v2.agents.recommendation_research.prompt import prompt
from recommender.graphs.recommendation_v2.models import serialize_chat_history
from recommender.tools import create_tavily_search_tool
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class RecommendationV2RecommendationResearchAgent:
    """Agent that researches one region using Tavily search results."""

    def __init__(
        self,
        *,
        llm: BaseChatModel,
        tavily_api_key: str,
    ) -> None:
        if not tavily_api_key.strip():
            raise ValueError("tavily_api_key must be provided for region research")

        self._prompt_template = prompt
        self._agent = create_agent(
            model=llm,
            tools=[create_tavily_search_tool(tavily_api_key)],
            response_format=RecommendationV2RecommendationResearchResult,
        )

    def _extract_output(self, result: Any) -> RecommendationV2RecommendationResearchResult:
        if isinstance(result, dict):
            structured_response = result.get("structured_response")
            if structured_response is not None:
                return RecommendationV2RecommendationResearchResult.model_validate(
                    structured_response,
                )

        return RecommendationV2RecommendationResearchResult.model_validate(result)

    def invoke(
        self,
        inputs: RecommendationV2RecommendationResearchInput,
    ) -> RecommendationV2RecommendationResearchResult:
        prompt_value = self._prompt_template.format_prompt(
            region_name=inputs.region_name,
            region_description=inputs.region_description,
            synthesized_user_query=inputs.synthesized_user_query,
            conversation=serialize_chat_history(inputs.conversation),
        )
        result = self._agent.invoke({"messages": prompt_value.to_messages()})
        logger.verbose("Raw region-research agent result: %s", result)
        return self._extract_output(result)
