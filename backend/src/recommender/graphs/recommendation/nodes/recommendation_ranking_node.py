from __future__ import annotations

from typing import Callable

from recommender.graphs.recommendation.models import RecommendationGraphState
from recommender.graphs.recommendation.models import RecommendationStatusEnum
from recommender.models.data_flow.user_preferences import UserLogisticalPreferences
from storage.stores.search_models import TravelSearchConstraints
from storage.stores.travel_destination_store import TravelDestinationStore
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

SEASON_TO_MONTHS: dict[str, tuple[str, ...]] = {
    "winter": ("dec", "jan", "feb"),
    "spring": ("mar", "apr", "may"),
    "summer": ("jun", "jul", "aug"),
    "autumn": ("sep", "oct", "nov"),
    "fall": ("sep", "oct", "nov"),
}
VALID_MONTHS = {
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
}
BUDGET_TIER_TO_MAX_COST: dict[str, float] = {
    "low": 600.0,
    "medium": 1200.0,
    "high": 2500.0,
}


def _extract_months(logistical_preferences: UserLogisticalPreferences) -> tuple[str, ...]:
    time_of_year_preferences = logistical_preferences.time_of_year
    if time_of_year_preferences is None:
        return ()

    if time_of_year_preferences.months:
        normalized_months: list[str] = []
        for month in time_of_year_preferences.months:
            normalized_month = month.lower().strip()
            if normalized_month in VALID_MONTHS and normalized_month not in normalized_months:
                normalized_months.append(normalized_month)
        if normalized_months:
            return tuple(normalized_months)

    if time_of_year_preferences.season:
        normalized_season = time_of_year_preferences.season.lower().strip()
        return SEASON_TO_MONTHS.get(normalized_season, ())

    return ()


def _to_search_constraints(logistical_preferences: UserLogisticalPreferences) -> TravelSearchConstraints:
    max_cost_per_week: float | None = None
    if logistical_preferences.price is not None:
        if logistical_preferences.price.max_cost_per_week is not None:
            max_cost_per_week = float(logistical_preferences.price.max_cost_per_week)
        elif logistical_preferences.price.budget_tier is not None:
            max_cost_per_week = BUDGET_TIER_TO_MAX_COST.get(logistical_preferences.price.budget_tier)

    min_popularity: float | None = None
    if logistical_preferences.popularity is not None:
        popularity_strength = float(logistical_preferences.popularity.strength) / 5.0
        if popularity_strength >= 0.6:
            min_popularity = popularity_strength

    return TravelSearchConstraints(
        max_cost_per_week=max_cost_per_week,
        min_popularity=min_popularity,
        months=_extract_months(logistical_preferences),
    )


def create_recommendation_ranking_node(
    travel_destination_store: TravelDestinationStore,
) -> Callable[[RecommendationGraphState], dict[str, object] | RecommendationGraphState]:
    """Create recommendation ranking node."""

    def recommendation_ranking_node(
        state: RecommendationGraphState,
    ) -> dict[str, object] | RecommendationGraphState:
        logger.info("Ranking recommendations based on user preferences...")

        recommendations = state.recommendation or []
        # this is a safeguard - ideally we should never reach this node if there are no recommendations
        if not recommendations:
            logger.info("No recommendations found, skipping ranking.")
            return {"status": RecommendationStatusEnum.ERROR}

        logistical_preferences = state.extracted_user_logistical_preferences
        if logistical_preferences is None or not logistical_preferences.are_preferences_present():
            logger.info("No logistical preferences found, preserving semantic ranking.")
            return {
                "recommendation": recommendations,
                "status": RecommendationStatusEnum.RECOMMENDATION_GENERATED,
            }

        constraints = _to_search_constraints(logistical_preferences)
        query = state.query if state.query is not None else state.user_input
        ranked_recommendations = travel_destination_store.hybrid_search(
            query=query,
            constraints=constraints,
        )
        if not ranked_recommendations:
            logger.warning("Hybrid search returned no results; keeping semantic ranking.")
            ranked_recommendations = recommendations

        logger.info("Applied logistical re-ranking to %s recommendations.", len(ranked_recommendations))

        return {
            "recommendation": ranked_recommendations,
            "status": RecommendationStatusEnum.RECOMMENDATION_GENERATED,
        }

    return recommendation_ranking_node
