from __future__ import annotations

from collections.abc import Callable

from recommender.graphs.recommendation_v2.agents.filter_extraction.budget.agent import (
    RecommendationV2BudgetFilterExtractionAgent,
)
from recommender.graphs.recommendation_v2.agents.filter_extraction.budget.models import (
    RecommendationV2BudgetFilterExtractionInput,
)
from recommender.graphs.recommendation_v2.filter_models import (
    RecommendationV2BudgetFilter,
    RecommendationV2TravelDestinationFilter,
)
from recommender.graphs.recommendation_v2.models import RecommendationV2GraphState
from recommender.graphs.recommendation_v2.utils.travel_destination_filter_node_utils import (
    latest_travel_destination_filter_from_history,
)
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def create_extract_budget_filter_node(
    budget_filter_extraction_agent: RecommendationV2BudgetFilterExtractionAgent,
) -> Callable[[RecommendationV2GraphState], dict[str, object]]:
    """Create node to extract recommendation_v2 budget filters from the current turn."""

    def extract_budget_filter_node(
        state: RecommendationV2GraphState,
    ) -> dict[str, object]:
        if state.history is None:
            raise RuntimeError(
                "Session history must be loaded before extracting recommendation_v2 budget filters"
            )

        base_filter = latest_travel_destination_filter_from_history(state.history)
        if base_filter is None:
            base_filter = RecommendationV2TravelDestinationFilter()

        logger.verbose(
            "Extracting recommendation_v2 budget filters for user_id=%s, session_id=%s with previous_cost_term=%s",
            state.session.user_id,
            state.session.session_id,
            base_filter.cost_term,
        )

        budget_result = budget_filter_extraction_agent.invoke(
            RecommendationV2BudgetFilterExtractionInput(
                current_user_request=state.user_request,
                previous_cost_term=base_filter.budget.cost_term,
            )
        )
        budget_filter = RecommendationV2BudgetFilter(
            min_cost_per_week=base_filter.budget.min_cost_per_week,
            cost_term=budget_result.cost_term,
            max_cost_per_week=base_filter.budget.max_cost_per_week,
        )

        logger.verbose(
            "Extracted recommendation_v2 budget filters for user_id=%s, session_id=%s: %s",
            state.session.user_id,
            state.session.session_id,
            budget_filter.cost_term,
        )

        return {
            "extracted_budget_filter": budget_filter,
        }

    return extract_budget_filter_node
