from __future__ import annotations

from langchain_core.tools import BaseTool
from langchain_core.tools import tool

from storage.stores.search_models import ScoredTravelDestination
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
    "jan", "feb", "mar", "apr", "may", "jun",
    "jul", "aug", "sep", "oct", "nov", "dec",
}


def _normalize_months(months: list[str]) -> tuple[str, ...]:
    normalized: list[str] = []
    for entry in months:
        cleaned = entry.lower().strip()
        if cleaned in SEASON_TO_MONTHS:
            for month in SEASON_TO_MONTHS[cleaned]:
                if month not in normalized:
                    normalized.append(month)
        elif cleaned in VALID_MONTHS and cleaned not in normalized:
            normalized.append(cleaned)
    return tuple(normalized)


class SearchResultsContainer:
    """Holds the last search results so the graph node can extract structured data."""

    def __init__(self) -> None:
        self.recommendations: list[ScoredTravelDestination] = []


def create_search_tool(
    store: TravelDestinationStore,
    result_container: SearchResultsContainer,
) -> BaseTool:
    """Create a LangChain tool that searches travel destinations.

    The LLM calls this tool with parameters extracted from the synthesized query.
    The tool handles exact keyword matching, hybrid ranking with logistics,
    and falls back to semantic search when no constraints are needed.
    """

    @tool
    def search_travel_destinations(
        query: str,
        destination_keywords: list[str] | None = None,
        max_cost_per_week: float | None = None,
        min_popularity: float | None = None,
        months: list[str] | None = None,
        limit: int = 10,
    ) -> str:
        """Search travel destinations matching the user's preferences.

        Combines semantic vector search with optional logistics constraints
        (budget, popularity, travel months) and optional exact keyword matching
        for specific destination/region names.

        Args:
            query: The natural language search query describing what the user wants.
            destination_keywords: Specific destination names or regions to match (e.g. ["Bavaria", "Algarve"]).
            max_cost_per_week: Maximum budget in EUR per week.
            min_popularity: Minimum popularity threshold 0.0-1.0 (higher = more popular).
            months: Preferred travel months or seasons (e.g. ["jun", "jul", "aug"] or ["summer"]).
            limit: Maximum number of results to return.
        """
        query = query.strip()
        logger.verbose(
            "search_travel_destinations called: query=%r, destination_keywords=%r, "
            "max_cost_per_week=%r, min_popularity=%r, months=%r, limit=%r",
            query, destination_keywords, max_cost_per_week, min_popularity, months, limit,
        )
        if not query:
            return "No query provided."

        destination_ids: list[str] = []
        if destination_keywords:
            for keyword in destination_keywords:
                try:
                    exact_matches = store.exact_text_search(keyword, limit=limit)
                    for match in exact_matches:
                        did = match.destination.id
                        if did not in destination_ids:
                            destination_ids.append(did)
                except ValueError:
                    logger.verbose("Empty keyword skipped: %r", keyword)

        destination_ids_or_none = destination_ids or None
        normalized_months = _normalize_months(months or [])
        has_cost = max_cost_per_week is not None
        has_popularity = min_popularity is not None
        has_months = len(normalized_months) > 0
        has_constraints = has_cost or has_popularity or has_months

        recommendations: list[ScoredTravelDestination]
        if has_constraints:
            constraints = TravelSearchConstraints(
                max_cost_per_week=max_cost_per_week,
                min_popularity=min_popularity,
                months=normalized_months,
            )
            recommendations = store.hybrid_search(
                query=query,
                constraints=constraints,
                limit=limit,
                destination_ids=destination_ids_or_none,
            )
            if not recommendations:
                logger.info("Hybrid returned empty; falling back to semantic")
                recommendations = store.semantic_search(
                    query,
                    limit=limit,
                    destination_ids=destination_ids_or_none,
                )
        else:
            recommendations = store.semantic_search(
                query,
                limit=limit,
                destination_ids=destination_ids_or_none,
            )

        result_container.recommendations = recommendations

        if not recommendations:
            return "No matching destinations found."

        lines: list[str] = []
        for item in recommendations:
            d = item.destination
            lines.append(
                f"- {d.region} (id={d.id}): {d.description[:100]}... "
                f"| cost={d.cost_per_week}/week | popularity={d.popularity:.2f} "
                f"| semantic_score={item.semantic_score:.4f} "
                f"| logistics_score={item.logistics_score:.4f} "
                f"| ranking_score={item.ranking_score:.4f}"
            )
        return "\n".join(lines)

    return search_travel_destinations
