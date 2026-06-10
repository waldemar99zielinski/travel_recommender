from __future__ import annotations

from recommender.graphs.recommendation_v2.filter_models import (
    ExplicitCostTermFilter,
    RecommendationV2TravelDestinationFilter,
)
from storage.stores.search_models import ScoredTravelDestination
from storage.stores.search_models import TravelCostStatistics


def apply_parent_region_filters(
    scored_destinations: list[ScoredTravelDestination],
    travel_destination_filter: RecommendationV2TravelDestinationFilter | None,
) -> list[ScoredTravelDestination]:
    if (
        travel_destination_filter is None
        or not travel_destination_filter.parent_region_filters
    ):
        return scored_destinations

    included_parent_regions = {
        region_filter.region_name
        for region_filter in travel_destination_filter.parent_region_filters
        if region_filter.type == "include"
    }
    excluded_parent_regions = {
        region_filter.region_name
        for region_filter in travel_destination_filter.parent_region_filters
        if region_filter.type == "exclude"
    }

    filtered_destinations = scored_destinations
    if included_parent_regions:
        return [
            scored_destination
            for scored_destination in scored_destinations
            if scored_destination.destination.parent_region in included_parent_regions
        ]
    if excluded_parent_regions:
        filtered_destinations = [
            scored_destination
            for scored_destination in filtered_destinations
            if scored_destination.destination.parent_region not in excluded_parent_regions
        ]

    return filtered_destinations


def resolve_weekly_cost(explicit_cost: ExplicitCostTermFilter) -> float:
    if explicit_cost.duration == "day":
        return explicit_cost.value * 7
    if explicit_cost.duration == "month":
        return explicit_cost.value / 4
    return explicit_cost.value


def resolve_budget_bounds(
    travel_destination_filter: RecommendationV2TravelDestinationFilter | None,
    cost_statistics: TravelCostStatistics | None,
) -> tuple[float | None, float | None]:
    if travel_destination_filter is None:
        return None, None

    cost_term = travel_destination_filter.budget.cost_term
    if cost_term is None:
        return (
            travel_destination_filter.budget.min_cost_per_week,
            travel_destination_filter.budget.max_cost_per_week,
        )

    if cost_term.explicit is not None:
        weekly_cost = resolve_weekly_cost(cost_term.explicit)
        if cost_term.explicit.operator == "min":
            return weekly_cost, None
        if cost_term.explicit.operator == "max":
            return None, weekly_cost

        return weekly_cost * 0.8, weekly_cost * 1.2

    if cost_term.inferred_level is None or cost_statistics is None:
        return None, None

    if cost_term.inferred_level == "low":
        return None, cost_statistics.percentile_50
    if cost_term.inferred_level == "medium":
        return cost_statistics.percentile_50, cost_statistics.percentile_75

    return cost_statistics.percentile_75, None


def apply_budget_filters(
    scored_destinations: list[ScoredTravelDestination],
    travel_destination_filter: RecommendationV2TravelDestinationFilter | None,
    cost_statistics: TravelCostStatistics | None,
) -> list[ScoredTravelDestination]:
    min_cost_per_week, max_cost_per_week = resolve_budget_bounds(
        travel_destination_filter,
        cost_statistics,
    )
    filtered_destinations = scored_destinations

    if min_cost_per_week is not None:
        filtered_destinations = [
            scored_destination
            for scored_destination in filtered_destinations
            if scored_destination.destination.cost_per_week >= min_cost_per_week
        ]
    if max_cost_per_week is not None:
        filtered_destinations = [
            scored_destination
            for scored_destination in filtered_destinations
            if scored_destination.destination.cost_per_week <= max_cost_per_week
        ]

    return filtered_destinations


def budget_filter_needs_statistics(
    travel_destination_filter: RecommendationV2TravelDestinationFilter | None,
) -> bool:
    if travel_destination_filter is None:
        return False

    cost_term = travel_destination_filter.budget.cost_term
    return cost_term is not None and cost_term.inferred_level is not None


__all__ = [
    "apply_budget_filters",
    "apply_parent_region_filters",
    "budget_filter_needs_statistics",
    "resolve_budget_bounds",
    "resolve_weekly_cost",
]
