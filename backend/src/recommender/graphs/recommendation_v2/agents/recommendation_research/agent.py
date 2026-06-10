from __future__ import annotations

import anyio

from recommender.graphs.recommendation_v2.agents.recommendation_research.models import (
    RecommendationV2RecommendationResearchInput,
)
from recommender.graphs.recommendation_v2.agents.recommendation_research.models import (
    RecommendationV2RecommendationResearchResult,
)
from recommender.graphs.recommendation_v2.models import serialize_chat_history
from recommender.models.llm.llm_config import LLMConfig
from tavily_agent_toolkit import ModelConfig
from tavily_agent_toolkit import ModelObject
from tavily_agent_toolkit import search_and_answer
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def _build_search_query(inputs: RecommendationV2RecommendationResearchInput) -> str:
    return "\n".join(
        [
            f"Research the travel region '{inputs.region_name}'.",
            (
                "Focus on the user's travel intent and what they can concretely do there: "
                f"{inputs.synthesized_user_query}."
            ),
            "Use the internal region description as grounding context:",
            inputs.region_description,
            "Conversation context:",
            serialize_chat_history(inputs.conversation),
            (
                "Return a concise travel-recommendation style answer grounded in web research, "
                "with attention to the most relevant travel images."
            ),
        ]
    )


def _build_tavily_model_config(llm_config: LLMConfig) -> ModelConfig:
    model_provider = "openai" if llm_config.provider == "chatgpt" else "ollama"

    return ModelConfig(
        model=ModelObject(
            model=llm_config.model,
            model_provider=model_provider,
            max_tokens=llm_config.max_tokens,
            api_key=llm_config.api_key,
        ),
        temperature=llm_config.temperature,
        timeout=llm_config.timeout_s,
    )


class RecommendationV2RecommendationResearchAgent:
    """Agent that researches one region using Tavily search results."""

    def __init__(
        self,
        *,
        llm_config: LLMConfig,
        tavily_api_key: str,
    ) -> None:
        if not tavily_api_key.strip():
            raise ValueError("tavily_api_key must be provided for region research")

        self._tavily_api_key = tavily_api_key
        self._model_config = _build_tavily_model_config(llm_config)

    async def _run_search_and_answer(
        self,
        inputs: RecommendationV2RecommendationResearchInput,
    ) -> RecommendationV2RecommendationResearchResult:
        search_query = _build_search_query(inputs)
        result = await search_and_answer(
            query=search_query,
            api_key=self._tavily_api_key,
            model_config=self._model_config,
            output_schema=RecommendationV2RecommendationResearchResult,
            max_number_of_subqueries=2,
            max_results=2,
            include_images=True,
        )

        # logger.verbose(
        #     "\n\nRegion research result for region=%s result:\n\n%s",
        #     inputs.region_name,
        #     result,
        # )

        answer = result.get("answer")
        # logger.verbose(
        #     "\n\nRegion research result for region=%s answer:\n\n%s",
        #     inputs.region_name,
        #     answer,
        # )

        images = []
        for r in result.get("results", []):
            images_object = r.get("images", [])
            for image in images_object:
                image_url = image.get("url")
                if image_url:
                    images.append(image_url)

        # logger.verbose(
        #     "\n\nRegion research result for region=%s urls:\n\n%s",
        #     inputs.region_name,
        # )

        response = RecommendationV2RecommendationResearchResult.model_validate(answer)

        response.image_urls = images

        return response

    def invoke(
        self,
        inputs: RecommendationV2RecommendationResearchInput,
    ) -> RecommendationV2RecommendationResearchResult:
        return anyio.run(self._run_search_and_answer, inputs)

    def invoke_async(
        self,
        inputs: RecommendationV2RecommendationResearchInput,
    ) -> RecommendationV2RecommendationResearchResult:
        return self._run_search_and_answer(inputs)
