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
            "You research one travel region and must return output that matches "
            "RecommendationV2RecommendationResearchResult.",
            f"Region to research: {inputs.region_name}.",
            (
                "Primary user intent to satisfy: "
                f"{inputs.synthesized_user_query}."
            ),
            "Use this internal region description as grounding context:",
            inputs.region_description,
            "Use this conversation context for nuance:",
            serialize_chat_history(inputs.conversation),
            "Research instructions:",
            (
                "Prioritize web results about the activities, scenery, atmosphere, seasonality, "
                "and trip style that best match the user's intent in this region."
            ),
            (
                "Prefer pages and images that show the specific experiences the user would likely "
                "care about, not generic region photos, maps, flags, logos, or unrelated landmarks."
            ),
            "Output rules:",
            "Return only the structured fields for RecommendationV2RecommendationResearchResult.",
            (
                "Write description as one polished paragraph of around 10 sentences, in a travel "
                "recommendation style, with concrete but non-hallucinated detail about what the user "
                "can do, see, and enjoy there. Do NOT include the references or sources. JUST DESCRIBE."
            ),
            (
                "Keep the description focused on the region's unique travel appeal and the user's intent"
            ),
            (
                "Keep the description grounded in the search results and the provided region "
                "description, and make it feel tailored to the user's request rather than generic."
            ),
            (
                "Do not mention sources, references, citations, web research, or the search process."
            ),
            (
                "For image_urls, include only relevant travel-photo URLs that visually match the "
                "user intent and the description; if none are relevant, return an empty list."
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

        # images = []
        # for r in result.get("results", []):
        #     images_object = r.get("images", [])
        #     for image in images_object:
        #         image_url = image.get("url")
        #         if image_url:
        #             images.append(image_url)


        logger.verbose(
            "\n\nRegion research result for region=%s answer:\n\n%s",
            inputs.region_name,
            answer,
        )
        # logger.verbose(
        #     "\n\nRegion research result for region=%s urls:\n\n%s",
        #     inputs.region_name,
        # )

        response = RecommendationV2RecommendationResearchResult.model_validate(answer)

        # response.image_urls = images[:6]

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
