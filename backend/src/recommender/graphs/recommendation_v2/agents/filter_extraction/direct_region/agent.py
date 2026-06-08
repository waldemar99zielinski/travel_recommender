from __future__ import annotations

from langchain_core.language_models import BaseChatModel

from recommender.graphs.recommendation_v2.agents.filter_extraction.direct_region.models import (
    RecommendationV2DirectRegionFilterExtractionInput,
)
from recommender.graphs.recommendation_v2.agents.filter_extraction.direct_region.models import (
    RecommendationV2DirectRegionFilterExtractionResult,
)
from recommender.graphs.recommendation_v2.agents.filter_extraction.direct_region.prompt import (
    prompt,
)
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class RecommendationV2DirectRegionFilterExtractionAgent:
    """Agent that extracts specific direct-region filters for recommendation_v2."""

    def __init__(
        self,
        *,
        llm: BaseChatModel,
    ) -> None:
        self._llm = llm
        self._prompt_template = prompt
        self._structured_output_llm = self._llm.with_structured_output(
            RecommendationV2DirectRegionFilterExtractionResult,
        )

    def invoke(
        self,
        inputs: RecommendationV2DirectRegionFilterExtractionInput,
    ) -> RecommendationV2DirectRegionFilterExtractionResult:
        prompt_value = self._prompt_template.format_prompt(
            current_user_request=inputs.current_user_request,
        )
        result = self._structured_output_llm.invoke(prompt_value.to_messages())
        logger.verbose("Raw direct-region filter-extraction structured LLM result: %s", result)
        return RecommendationV2DirectRegionFilterExtractionResult.model_validate(result)
