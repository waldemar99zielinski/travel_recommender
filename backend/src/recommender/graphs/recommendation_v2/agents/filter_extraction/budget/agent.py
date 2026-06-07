from __future__ import annotations

from langchain_core.language_models import BaseChatModel

from recommender.graphs.recommendation_v2.agents.filter_extraction.budget.models import (
    RecommendationV2BudgetFilterExtractionInput,
)
from recommender.graphs.recommendation_v2.agents.filter_extraction.budget.models import (
    RecommendationV2BudgetFilterExtractionResult,
)
from recommender.graphs.recommendation_v2.agents.filter_extraction.budget.prompt import (
    prompt,
)
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class RecommendationV2BudgetFilterExtractionAgent:
    """Agent that extracts budget filters for recommendation_v2."""

    def __init__(
        self,
        *,
        llm: BaseChatModel,
    ) -> None:
        self._llm = llm
        self._prompt_template = prompt
        self._structured_output_llm = self._llm.with_structured_output(
            RecommendationV2BudgetFilterExtractionResult,
        )

    def invoke(
        self,
        inputs: RecommendationV2BudgetFilterExtractionInput,
    ) -> RecommendationV2BudgetFilterExtractionResult:
        prompt_value = self._prompt_template.format_prompt(
            current_user_request=inputs.current_user_request,
            previous_budget_filter=RecommendationV2BudgetFilterExtractionResult(
                cost_term=inputs.previous_cost_term,
            ).model_dump_json(indent=2, exclude_none=True),
        )
        result = self._structured_output_llm.invoke(prompt_value.to_messages())
        logger.verbose("Raw budget filter-extraction structured LLM result: %s", result)
        return RecommendationV2BudgetFilterExtractionResult.model_validate(result)
