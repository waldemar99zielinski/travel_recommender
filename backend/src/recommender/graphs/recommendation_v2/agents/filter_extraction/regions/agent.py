from __future__ import annotations

from langchain_core.language_models import BaseChatModel

from recommender.graphs.recommendation_v2.agents.filter_extraction.regions.models import (
    RecommendationV2RegionsFilterExtractionInput,
)
from recommender.graphs.recommendation_v2.agents.filter_extraction.regions.models import (
    RecommendationV2RegionsFilterExtractionResult,
)
from recommender.graphs.recommendation_v2.agents.filter_extraction.regions.prompt import (
    prompt,
)
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class RecommendationV2RegionsFilterExtractionAgent:
    """Agent that extracts region filters for recommendation_v2."""

    def __init__(
        self,
        *,
        llm: BaseChatModel,
    ) -> None:
        self._llm = llm
        self._prompt_template = prompt
        self._structured_output_llm = self._llm.with_structured_output(
            RecommendationV2RegionsFilterExtractionResult,
        )

    def invoke(
        self,
        inputs: RecommendationV2RegionsFilterExtractionInput,
    ) -> RecommendationV2RegionsFilterExtractionResult:
        prompt_value = self._prompt_template.format_prompt(
            current_user_request=inputs.current_user_request,
        )
        result = self._structured_output_llm.invoke(prompt_value.to_messages())
        logger.verbose("Raw regions filter-extraction structured LLM result: %s", result)
        return RecommendationV2RegionsFilterExtractionResult.model_validate(result)
