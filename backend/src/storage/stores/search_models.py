from __future__ import annotations

from dataclasses import dataclass

from storage.models.travel_destination import TravelDestinationRecord


@dataclass(frozen=True, slots=True)
class TravelSearchConstraints:
    """Optional business constraints used in hybrid ranking."""

    max_cost_per_week: float | None = None
    min_popularity: float | None = None
    months: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ScoredTravelDestination:
    """Search result with semantic and logistics scoring details."""

    destination: TravelDestinationRecord
    embedding_distance: float
    semantic_score: float
    logistics_score: float
    ranking_score: float
