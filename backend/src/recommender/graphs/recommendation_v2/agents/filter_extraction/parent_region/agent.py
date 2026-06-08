from __future__ import annotations

from langchain_core.language_models import BaseChatModel

from recommender.graphs.recommendation_v2.agents.filter_extraction.parent_region.models import (
    RecommendationV2ParentRegionFilterExtractionInput,
)
from recommender.graphs.recommendation_v2.agents.filter_extraction.parent_region.models import (
    RecommendationV2ParentRegionFilterExtractionResult,
)
from recommender.graphs.recommendation_v2.agents.filter_extraction.parent_region.prompt import (
    prompt,
)
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class RecommendationV2ParentRegionFilterExtractionAgent:
    """Agent that extracts broad parent-region (continent-level) filters for recommendation_v2."""

    def __init__(
        self,
        *,
        llm: BaseChatModel,
    ) -> None:
        self._llm = llm
        self._prompt_template = prompt
        self._structured_output_llm = self._llm.with_structured_output(
            RecommendationV2ParentRegionFilterExtractionResult,
        )

    def invoke(
        self,
        inputs: RecommendationV2ParentRegionFilterExtractionInput,
    ) -> RecommendationV2ParentRegionFilterExtractionResult:
        prompt_value = self._prompt_template.format_prompt(
            current_user_request=inputs.current_user_request,
        )
        result = self._structured_output_llm.invoke(prompt_value.to_messages())
        logger.verbose("Raw parent-region filter-extraction structured LLM result: %s", result)
        return RecommendationV2ParentRegionFilterExtractionResult.model_validate(result)
