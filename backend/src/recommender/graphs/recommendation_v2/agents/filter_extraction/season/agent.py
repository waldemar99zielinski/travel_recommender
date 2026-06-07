from __future__ import annotations

from langchain_core.language_models import BaseChatModel

from recommender.graphs.recommendation_v2.agents.filter_extraction.season.models import (
    RecommendationV2SeasonFilterExtractionInput,
)
from recommender.graphs.recommendation_v2.agents.filter_extraction.season.models import (
    RecommendationV2SeasonFilterExtractionResult,
)
from recommender.graphs.recommendation_v2.agents.filter_extraction.season.prompt import (
    prompt,
)
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class RecommendationV2SeasonFilterExtractionAgent:
    """Agent that extracts season and month filters for recommendation_v2."""

    def __init__(
        self,
        *,
        llm: BaseChatModel,
    ) -> None:
        self._llm = llm
        self._prompt_template = prompt
        self._structured_output_llm = self._llm.with_structured_output(
            RecommendationV2SeasonFilterExtractionResult,
        )

    def invoke(
        self,
        inputs: RecommendationV2SeasonFilterExtractionInput,
    ) -> RecommendationV2SeasonFilterExtractionResult:
        prompt_value = self._prompt_template.format_prompt(
            current_user_request=inputs.current_user_request,
            previous_season_filter=RecommendationV2SeasonFilterExtractionResult(
                season=inputs.previous_season,
                months=inputs.previous_months,
            ).model_dump_json(indent=2, exclude_none=True),
        )
        result = self._structured_output_llm.invoke(prompt_value.to_messages())
        logger.verbose("Raw season filter-extraction structured LLM result: %s", result)
        return RecommendationV2SeasonFilterExtractionResult.model_validate(result)
