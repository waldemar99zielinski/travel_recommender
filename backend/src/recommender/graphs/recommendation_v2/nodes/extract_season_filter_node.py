from __future__ import annotations

from collections.abc import Callable

from recommender.graphs.recommendation_v2.agents.filter_extraction.season.agent import (
    RecommendationV2SeasonFilterExtractionAgent,
)
from recommender.graphs.recommendation_v2.agents.filter_extraction.season.models import (
    RecommendationV2SeasonFilterExtractionInput,
)
from recommender.graphs.recommendation_v2.filter_models import (
    RecommendationV2SeasonalityFilter,
    RecommendationV2TravelDestinationFilter,
)
from recommender.graphs.recommendation_v2.models import RecommendationV2GraphState
from recommender.graphs.recommendation_v2.nodes.travel_destination_filter_node_utils import (
    latest_travel_destination_filter_from_history,
)
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def create_extract_season_filter_node(
    season_filter_extraction_agent: RecommendationV2SeasonFilterExtractionAgent,
) -> Callable[[RecommendationV2GraphState], dict[str, object]]:
    """Create node to extract recommendation_v2 season and month filters from the current turn."""

    def extract_season_filter_node(
        state: RecommendationV2GraphState,
    ) -> dict[str, object]:
        if state.history is None:
            raise RuntimeError(
                "Session history must be loaded before extracting recommendation_v2 season filters"
            )

        base_filter = latest_travel_destination_filter_from_history(state.history)
        if base_filter is None:
            base_filter = RecommendationV2TravelDestinationFilter()

        logger.verbose(
            "Extracting recommendation_v2 season filters for user_id=%s, session_id=%s with previous_season=%s, previous_months=%s",
            state.session.user_id,
            state.session.session_id,
            base_filter.season,
            base_filter.months,
        )

        season_result = season_filter_extraction_agent.invoke(
            RecommendationV2SeasonFilterExtractionInput(
                current_user_request=state.user_request,
                previous_season=base_filter.seasonality.season,
                previous_months=base_filter.seasonality.months,
            )
        )
        seasonality_filter = RecommendationV2SeasonalityFilter(
            season=season_result.season,
            months=season_result.months,
        )

        logger.verbose(
            "Extracted recommendation_v2 season filters for user_id=%s, session_id=%s: season=%s, months=%s",
            state.session.user_id,
            state.session.session_id,
            seasonality_filter.season,
            seasonality_filter.months,
        )

        return {
            "extracted_seasonality_filter": seasonality_filter,
        }

    return extract_season_filter_node
