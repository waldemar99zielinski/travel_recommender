from __future__ import annotations

from bisect import bisect_left
from collections import Counter
from collections import defaultdict
from dataclasses import dataclass

from pydantic import BaseModel
from pydantic import Field

from region_description_generation.paths import ensure_src_path

ensure_src_path()

from storage.models.travel_destination import TravelDestinationRecord

MONTH_FIELDS: tuple[str, ...] = (
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
)

INTEREST_FIELDS: tuple[str, ...] = (
    "nature",
    "hiking",
    "beach",
    "watersports",
    "entertainment",
    "wintersports",
    "culture",
    "culinary",
    "architecture",
    "shopping",
)

PLACEHOLDER_DESCRIPTION_FRAGMENTS: tuple[str, ...] = (
    "offers a unique travel experience",
    "nature enthusiasts will appreciate",
    "visitors can explore the rich local heritage",
    "beautiful beaches provide the perfect setting",
    "scenic trails offer great opportunities",
)

MONTH_LABELS: dict[str, str] = {
    "jan": "January",
    "feb": "February",
    "mar": "March",
    "apr": "April",
    "may": "May",
    "jun": "June",
    "jul": "July",
    "aug": "August",
    "sep": "September",
    "oct": "October",
    "nov": "November",
    "dec": "December",
}

INTEREST_LABELS: dict[str, str] = {
    "nature": "nature",
    "hiking": "hiking",
    "beach": "beaches",
    "watersports": "watersports",
    "entertainment": "entertainment",
    "wintersports": "winter sports",
    "culture": "culture",
    "culinary": "food and drink",
    "architecture": "architecture",
    "shopping": "shopping",
}

SYSTEM_PROMPT_TEMPLATE = """
You generate destination descriptions for travel-region embeddings.

Catalog analysis:
{catalog_summary}

Your job:
- Perform a web-backed deep search for the supplied travel region.
- First infer what kind of region it is from the database context: country, subnational macro-region, island group, cross-border area, or another tourism region type.
- Then research the region at that level instead of assuming it is a city or a single attraction.
- Use the database scores as grounding signals. If the data says hiking, beaches, culture, or winter sports are strong or weak, reflect that emphasis proportionally.
- Identify the region by name clearly and describe it as a real place with a distinct landscape, settlement pattern, culture, and travel identity.

Output rules:
- Return only the final description in the `description` field.
- Write 700 to 1000 words in plain text with no markdown, bullets, or citations.
- Make it embedding-friendly: dense with concrete geography, atmosphere, signature places, activities, culture, cuisine, architecture, and seasonal character.
- Include the exact region name naturally in the opening sentence and again where useful later in the description.
- Explain what the region is most famous for, what travelers most commonly do there, and what experiences define it beyond a generic summary.
- Mention the most important cities, towns, villages, or resort areas that help a traveler understand the region.
- Describe the recurring built environment and architectural character that appears across the region, such as historic centers, port districts, chalet villages, spa towns, vineyard settlements, fortified towns, fishing harbors, modern resort strips, religious complexes, or other reappearing building patterns when relevant.
- Mention recurring annual or seasonal events, festivals, pilgrimages, harvest traditions, markets, sporting events, or cultural celebrations only when they are well-established and structurally characteristic of the region.
- Show how landscapes, settlements, activities, and traditions connect to each other so the description reads as one rich regional portrait rather than a list.
- Prefer durable facts over temporary or fast-changing details.
- If the region spans multiple countries or a broad territory, say so clearly.
- Avoid fluff, generic travel-ad language, and phrases like "offers a unique travel experience".
- Avoid hotel-specific, one-off event-specific, or price-specific claims unless they are structurally characteristic of the region.
""".strip()


class RegionDescriptionResult(BaseModel):
    """Structured description returned by the research agent."""

    description: str = Field(
        ...,
        description="Detailed destination description suitable for embedding generation.",
    )


@dataclass(slots=True)
class RegionResearchContext:
    """Prompt context assembled from the stored travel destination catalog."""

    destination_id: str
    region: str
    parent_region: str
    current_description: str
    sibling_regions: list[str]
    strongest_months: list[str]
    strongest_interests: list[str]
    cost_per_week: float
    popularity: float
    relative_cost: str
    relative_popularity: str

    def to_prompt_payload(self) -> dict[str, object]:
        """Serialize research context into an LLM-friendly payload."""
        return {
            "destination_id": self.destination_id,
            "region": self.region,
            "parent_region": self.parent_region,
            "current_description": self.current_description,
            "sibling_regions": self.sibling_regions,
            "strongest_months": self.strongest_months,
            "strongest_interests": self.strongest_interests,
            "cost_per_week": self.cost_per_week,
            "popularity": self.popularity,
            "relative_cost": self.relative_cost,
            "relative_popularity": self.relative_popularity,
        }


@dataclass(slots=True)
class RegionCatalogAnalysis:
    """Summary of the persisted destination catalog used to ground prompting."""

    records_by_id: dict[str, TravelDestinationRecord]
    sibling_regions_by_parent: dict[str, list[str]]
    parent_counts: dict[str, int]
    sorted_costs: list[float]
    sorted_popularity: list[float]

    def build_region_context(self, record: TravelDestinationRecord) -> RegionResearchContext:
        """Build per-region prompt context from the analyzed catalog."""
        siblings = [
            region_name
            for region_name in self.sibling_regions_by_parent.get(record.parent_region, [])
            if region_name != record.region
        ]

        return RegionResearchContext(
            destination_id=record.id,
            region=record.region,
            parent_region=record.parent_region,
            current_description=record.description,
            sibling_regions=siblings[:8],
            strongest_months=top_month_labels(record),
            strongest_interests=top_interest_labels(record),
            cost_per_week=record.cost_per_week,
            popularity=record.popularity,
            relative_cost=relative_cost_label(record.cost_per_week, self.sorted_costs),
            relative_popularity=relative_popularity_label(record.popularity, self.sorted_popularity),
        )

    def to_prompt_summary(self) -> str:
        """Return a compact summary of catalog structure for the system prompt."""
        destination_count = len(self.records_by_id)
        parent_region_count = len(self.parent_counts)
        most_common_parents = ", ".join(
            f"{parent} ({count})"
            for parent, count in sorted(
                self.parent_counts.items(),
                key=lambda item: (-item[1], item[0]),
            )[:12]
        )

        sample_regions = ", ".join(
            record.region
            for record in sorted(
                self.records_by_id.values(),
                key=lambda item: (item.parent_region, item.region),
            )[:12]
        )

        return (
            f"The database contains {destination_count} persisted travel regions across "
            f"{parent_region_count} parent buckets. "
            f"The stored regions are mostly countries, large subnational macro-regions, island groups, "
            f"and cross-border tourism areas rather than cities. "
            f"Largest parent buckets include {most_common_parents}. "
            f"Sample regions include {sample_regions}."
        )


def analyze_region_catalog(records: list[TravelDestinationRecord]) -> RegionCatalogAnalysis:
    """Analyze the persisted destination catalog before generation."""
    if not records:
        raise ValueError("No travel destinations were loaded from storage.")

    sibling_regions_by_parent: dict[str, list[str]] = defaultdict(list)
    parent_counts = Counter[str]()
    costs: list[float] = []
    popularity_values: list[float] = []

    for record in records:
        sibling_regions_by_parent[record.parent_region].append(record.region)
        parent_counts[record.parent_region] += 1
        costs.append(record.cost_per_week)
        popularity_values.append(record.popularity)

    for regions in sibling_regions_by_parent.values():
        regions.sort()

    return RegionCatalogAnalysis(
        records_by_id={record.id: record for record in records},
        sibling_regions_by_parent=dict(sibling_regions_by_parent),
        parent_counts=dict(parent_counts),
        sorted_costs=sorted(costs),
        sorted_popularity=sorted(popularity_values),
    )


def is_placeholder_description(description: str | None) -> bool:
    """Return whether the current description is blank or clearly generic."""
    if description is None:
        return True

    normalized = description.strip().lower()
    if not normalized:
        return True

    return any(fragment in normalized for fragment in PLACEHOLDER_DESCRIPTION_FRAGMENTS)


def top_month_labels(record: TravelDestinationRecord, *, limit: int = 4) -> list[str]:
    """Return the strongest months for the destination based on stored scores."""
    scored_months = sorted(
        ((month, float(getattr(record, month))) for month in MONTH_FIELDS),
        key=lambda item: (-item[1], item[0]),
    )
    filtered = [MONTH_LABELS[month] for month, score in scored_months if score >= 0.75]
    if filtered:
        return filtered[:limit]
    return [MONTH_LABELS[month] for month, _score in scored_months[:limit]]


def top_interest_labels(record: TravelDestinationRecord, *, limit: int = 5) -> list[str]:
    """Return the strongest destination interests based on stored scores."""
    scored_interests = sorted(
        ((interest, float(getattr(record, interest))) for interest in INTEREST_FIELDS),
        key=lambda item: (-item[1], item[0]),
    )
    filtered = [INTEREST_LABELS[interest] for interest, score in scored_interests if score >= 0.75]
    if filtered:
        return filtered[:limit]
    return [INTEREST_LABELS[interest] for interest, _score in scored_interests[:limit]]


def relative_cost_label(cost_per_week: float, sorted_costs: list[float]) -> str:
    """Describe a region's cost relative to the stored catalog."""
    percentile = percentile_rank(cost_per_week, sorted_costs)
    if percentile <= 0.2:
        return "among the cheaper regions in the database"
    if percentile <= 0.4:
        return "below the middle of the database cost range"
    if percentile < 0.8:
        return "around the middle of the database cost range"
    return "among the more expensive regions in the database"


def relative_popularity_label(popularity: float, sorted_popularity: list[float]) -> str:
    """Describe a region's popularity relative to the stored catalog."""
    percentile = percentile_rank(popularity, sorted_popularity)
    if percentile <= 0.2:
        return "among the less popular regions in the database"
    if percentile <= 0.4:
        return "slightly below the middle of the database popularity range"
    if percentile < 0.8:
        return "around the middle of the database popularity range"
    return "among the more popular regions in the database"


def percentile_rank(value: float, sorted_values: list[float]) -> float:
    """Return the percentile rank of a value inside a sorted list."""
    if not sorted_values:
        return 0.5
    position = bisect_left(sorted_values, value)
    return position / max(len(sorted_values) - 1, 1)
