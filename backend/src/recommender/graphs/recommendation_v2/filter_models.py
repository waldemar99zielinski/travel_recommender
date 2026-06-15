from __future__ import annotations

import json
from typing import Any
from typing import Literal

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator
from pydantic import model_validator

MonthCode = Literal[
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
]
RegionFilterType = Literal["include", "exclude"]
TravelDestinationRegionField = Literal["parent_region", "region"]
SeasonCode = Literal["winter", "spring", "summer", "autumn"]

AbstractCostTerm = Literal["low", "medium", "high"]
CostTermOperator = Literal["max", "min", "around"]
CostTermDuration = Literal["day", "week", "month"]

ALLOWED_RECOMMENDATION_V2_PARENT_REGION_NAMES: tuple[str, ...] = (
    "Africa",
    "Antarctica",
    "Asia",
    "Australia",
    "Europe",
    "North America",
    "South America",
)

ALLOWED_RECOMMENDATION_V2_REGION_NAMES: tuple[str, ...] = (
    "China East (Shanghai region)",
    "Patagonia",
    "Lebanon and Syria",
    "Venezuela",
    "Baltic states",
    "Australia South",
    "India West",
    "England and Wales",
    "China Northwest (Shaanxi to Xinjiang)",
    "Uzbekistan and Turkmenistan",
    "Papua New Guinea",
    "Kyrgyzstan and Tajikistan",
    "Russia East",
    "Sri Lanka",
    "Finland",
    "Sahel West",
    "Canada Atlantic Provinces",
    "Colombia",
    "Czech Republic and Slovakia",
    "Ireland and Northern Ireland",
    "China Southwest (Guangxi to Tibet)",
    "Cuba",
    "North Korea",
    "Brazil Northeast",
    "Algeria",
    "France",
    "Brazil Southeast",
    "Slovenia and Croatia",
    "Comoros, Mayotte, Mauritius, Reunion",
    "Maldives",
    "Israel",
    "Iceland and Faroe Islands",
    "Antarctica and South Atlantic",
    "Kenya",
    "USA Midwest",
    "Madagascar",
    "Uganda, Rwanda and Burundi",
    "India Northeast and Bangladesh",
    "Guatemala and Belize",
    "Greater Antilles without Cuba",
    "Philippines",
    "Jordan and Palestina",
    "Chile North and Central",
    "Cyprus",
    "India Himalayan North and Plains",
    "Turkey",
    "Saudi-Arabia",
    "Canada North",
    "Portugal, islands",
    "Greece, islands",
    "Melanesia",
    "Romania, Bulgaria and Macedonia",
    "Scotland",
    "Eritrea, Djibouti, Ethiopia",
    "Russia South",
    "Canada Ontario",
    "West Malaysia and Singapur",
    "Paraguay",
    "Polynesia",
    "Libya",
    "Australia West",
    "USA Rocky Mountains",
    "Spain, Canary islands",
    "Belarus, Ukraine and Moldova",
    "China North (Beijing region)",
    "United Arab Emirates",
    "Mexico Baja California",
    "Sumatra and Java",
    "Portugal, mainland",
    "India South",
    "USA Southwest",
    "Greece, mainland",
    "West Africa",
    "Benelux",
    "Taiwan",
    "Canada British Columbia",
    "Corsica and Sardinia",
    "Caucasus",
    "Bhutan",
    "USA Pacific Northwest",
    "Northern Mexico",
    "Canada Prairies",
    "Guianas",
    "Switzerland and Liechtenstein",
    "Zambia and Malawi",
    "Uruguay",
    "Oman and Yemen",
    "Mozambique and Zimbabwe",
    "Brazil Central West",
    "USA Texas",
    "Argentina Central",
    "Thailand South",
    "Germany",
    "Borneo",
    "USA Florida",
    "USA South",
    "South Korea",
    "Spain, mainland",
    "Mexico Pacific Coast",
    "Namibia",
    "Qatar and Bahrain",
    "Canada Quebec",
    "Australia Northeast",
    "Egypt",
    "Afghanistan",
    "Iran",
    "Honduras and El Salvador",
    "Micronesia",
    "Iraq and Kuwait",
    "Thailand North and Laos",
    "South Africa",
    "Peru",
    "Kazakhstan",
    "Bahamas, Turks and Caicos Islands",
    "Japan",
    "Sweden and Denmark",
    "Russia Central",
    "Mongolia",
    "Vietnam and Cambodia",
    "Mexico Bajio and Central Mexico",
    "Spain, Balearic Islands",
    "New Zealand",
    "Ecuador",
    "China Northeast (Liaoning to Heilongjiang)",
    "Brazil North",
    "Hungary",
    "Argentina North",
    "Norway",
    "Sahel East",
    "Botswana",
    "USA Hawaii",
    "China South-central (Sichuan to Anhui)",
    "Pakistan",
    "China Southeast (Hainan to Fujian, incl. Hong Kong)",
    "Lesser Antilles",
    "India East",
    "Austria",
    "Central Africa",
    "Brazil South",
    "Bolivia",
    "Bali and Lombok",
    "Russia West",
    "USA California",
    "USA Great Plains",
    "Panama",
    "Mexico Yucatan",
    "Tunisia",
    "Morocco",
    "USA Alaska",
    "Indonesian islands west of Lombok",
    "Myanmar",
    "Albania, Kosovo",
    "USA Mid-Atlantic",
    "Nicaragua",
    "Serbia, Bosnia and Herzegovina, Montenegro",
    "Nepal",
    "Tanzania",
    "Poland",
    "Italy and Malta",
    "Greenland",
    "Costa Rica",
    "USA New England",
    "Somalia",
)

_ALLOWED_RECOMMENDATION_V2_PARENT_REGION_NAME_SET = frozenset(
    ALLOWED_RECOMMENDATION_V2_PARENT_REGION_NAMES,
)
_ALLOWED_RECOMMENDATION_V2_REGION_NAME_SET = frozenset(
    ALLOWED_RECOMMENDATION_V2_REGION_NAMES,
)

class ExplicitCostTermFilter(BaseModel):
    """Explicit cost term filter when the user directly mentions a concrete money amount."""

    value: float = Field(
        ...,
        ge=0.0,
        description="Exact numeric money amount provided by the user. For example, 200 for '200 euro per day' or 700 for '700 for the trip'.",
    )
    operator: CostTermOperator = Field(
        ...,
        description="Operator indicating whether the explicit amount is an upper bound (max), lower bound (min), or approximate target (around).",
    )
    duration: CostTermDuration = Field(
        ...,
        description="Duration that the explicit amount applies to. If the user gives a full-trip amount, resolve it to week because the system assumes a trip lasts one week.",
    )

class CostTerm(BaseModel):
    """Resolved cost term filter that combines explicit cost information and inferred qualitative budget levels."""

    explicit: ExplicitCostTermFilter | None = Field(
        None,
        description="Explicit cost term filter if the user provided a direct concrete money amount.",
    )
    inferred_level: AbstractCostTerm | None = Field(
        None,
        description="Inferred qualitative budget level (low, medium, high) based on the user's request, even if they did not explicitly mention it.",
    )

    @model_validator(mode="after")
    def validate_single_cost_representation(self) -> CostTerm:
        if self.explicit is not None and self.inferred_level is not None:
            raise ValueError("cost_term must contain either explicit or inferred_level, not both")
        if self.explicit is None and self.inferred_level is None:
            raise ValueError("cost_term must contain either explicit or inferred_level")

        return self

class RecommendationV2RegionFilter(BaseModel):
    """Region constraint extracted for recommendation_v2."""

    field_name: TravelDestinationRegionField = Field(
        ...,
        description="Catalog field constrained by this filter: parent_region for broad regions or region for direct mapped regions",
    )

    region_name: str = Field(
        ...,
        min_length=1,
        description="Exact allowed catalog value for the selected region field",
    )
    type: RegionFilterType = Field(
        ...,
        description="Whether the region should be included or excluded",
    )

    @model_validator(mode="before")
    @classmethod
    def populate_legacy_field_name(cls, value: Any) -> Any:
        if not isinstance(value, dict) or "field_name" in value:
            return value

        legacy_value = dict(value)
        legacy_value["field_name"] = "parent_region"
        return legacy_value

    @model_validator(mode="after")
    def validate_supported_region_name(self) -> RecommendationV2RegionFilter:
        allowed_region_names = (
            _ALLOWED_RECOMMENDATION_V2_PARENT_REGION_NAME_SET
            if self.field_name == "parent_region"
            else _ALLOWED_RECOMMENDATION_V2_REGION_NAME_SET
        )
        if self.region_name not in allowed_region_names:
            raise ValueError(
                f"region_name '{self.region_name}' is not allowed for field_name '{self.field_name}'"
            )

        return self


class RecommendationV2SeasonalityFilter(BaseModel):
    """Structured seasonality constraints extracted for recommendation_v2."""

    season: SeasonCode | None = Field(
        None,
        description="Requested travel season, for example winter, spring, summer, or autumn",
    )
    months: list[MonthCode] = Field(
        default_factory=list,
        description="Requested travel months, for example jan, feb, or oct",
    )

    def has_any_constraints(self) -> bool:
        """Return whether any seasonality constraint is present."""

        return self.season is not None or bool(self.months)

    def serialize(self) -> dict[str, object]:
        """Serialize only meaningful seasonality fields."""

        serialized: dict[str, object] = {}
        if self.season is not None:
            serialized["season"] = self.season
        if self.months:
            serialized["months"] = self.months

        return serialized


class RecommendationV2BudgetFilter(BaseModel):
    """Structured budget constraints extracted for recommendation_v2."""

    min_cost_per_week: float | None = Field(
        None,
        ge=0.0,
        description="Minimum acceptable weekly cost if the user explicitly sets a lower bound",
    )
    cost_term: CostTerm | None = Field(
        None,
        description="Resolved qualitative budget level: low, medium, or high",
    )
    max_cost_per_week: float | None = Field(
        None,
        ge=0.0,
        description="Maximum acceptable weekly cost if the user explicitly sets a budget cap",
    )

    @field_validator("cost_term", mode="before")
    @classmethod
    def normalize_empty_cost_term(cls, value: Any) -> Any:
        return normalize_optional_cost_term(value)

    @model_validator(mode="after")
    def validate_cost_range(self) -> RecommendationV2BudgetFilter:
        if (
            self.min_cost_per_week is not None
            and self.max_cost_per_week is not None
            and self.min_cost_per_week > self.max_cost_per_week
        ):
            raise ValueError("min_cost_per_week must be less than or equal to max_cost_per_week")

        return self

    def has_any_constraints(self) -> bool:
        """Return whether any budget constraint is present."""

        return any(
            (
                self.min_cost_per_week is not None,
                self.cost_term is not None,
                self.max_cost_per_week is not None,
            )
        )

    def serialize(self) -> dict[str, object]:
        """Serialize only meaningful budget fields."""

        serialized: dict[str, object] = {}
        if self.min_cost_per_week is not None:
            serialized["min_cost_per_week"] = self.min_cost_per_week
        if self.cost_term is not None:
            serialized["cost_term"] = self.cost_term.model_dump(exclude_none=True)
        if self.max_cost_per_week is not None:
            serialized["max_cost_per_week"] = self.max_cost_per_week

        return serialized


class RecommendationV2TravelDestinationFilter(BaseModel):
    """Structured travel-destination filters grouped by filter category."""

    parent_region_filters: list[RecommendationV2RegionFilter] = Field(
        default_factory=list,
        description="Parent-region filters with explicit include or exclude intent",
    )
    seasonality: RecommendationV2SeasonalityFilter = Field(
        default_factory=RecommendationV2SeasonalityFilter,
        description="Season and month constraints for the request",
    )
    budget: RecommendationV2BudgetFilter = Field(
        default_factory=RecommendationV2BudgetFilter,
        description="Budget constraints for the request",
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_payload(cls, value: Any) -> Any:
        return value

    @property
    def season(self) -> SeasonCode | None:
        """Return the selected season from the seasonality category."""

        return self.seasonality.season

    @property
    def months(self) -> list[MonthCode]:
        """Return the selected months from the seasonality category."""

        return self.seasonality.months

    @property
    def cost_term(self) -> CostTerm | None:
        """Return the resolved budget term from the budget category."""

        return self.budget.cost_term

    @property
    def min_cost_per_week(self) -> float | None:
        """Return the minimum weekly budget from the budget category."""

        return self.budget.min_cost_per_week

    @property
    def max_cost_per_week(self) -> float | None:
        """Return the maximum weekly budget from the budget category."""

        return self.budget.max_cost_per_week

    def has_any_constraints(self) -> bool:
        """Return whether at least one filter constraint is present."""

        return any(
            (
                bool(self.parent_region_filters),
                self.seasonality.has_any_constraints(),
                self.budget.has_any_constraints(),
            )
        )

    def serialize(self) -> dict[str, object]:
        """Serialize the canonical persisted filter object."""

        serialized: dict[str, object] = {}
        if self.parent_region_filters:
            serialized["parent_region_filters"] = [
                region.model_dump() for region in self.parent_region_filters
            ]
        seasonality = self.seasonality.serialize()
        if seasonality:
            serialized["seasonality"] = seasonality

        budget = self.budget.serialize()
        if budget:
            serialized["budget"] = budget

        return serialized


def serialize_travel_destination_filter(
    travel_destination_filter: RecommendationV2TravelDestinationFilter | None,
) -> str:
    """Serialize a filter into a compact prompt-friendly string."""

    if travel_destination_filter is None or not travel_destination_filter.has_any_constraints():
        return "None"

    return json.dumps(travel_destination_filter.serialize(), indent=2)


def normalize_optional_cost_term(value: Any) -> Any:
    """Treat an empty cost_term object as an absent budget term."""

    if not isinstance(value, dict):
        return value

    explicit = value.get("explicit")
    inferred_level = value.get("inferred_level")
    if explicit is None and inferred_level is None:
        return None

    return value


__all__ = [
    "CostTerm",
    "CostTermDuration",
    "CostTermOperator",
    "ExplicitCostTermFilter",
    "MonthCode",
    "ALLOWED_RECOMMENDATION_V2_PARENT_REGION_NAMES",
    "ALLOWED_RECOMMENDATION_V2_REGION_NAMES",
    "RecommendationV2BudgetFilter",
    "RecommendationV2RegionFilter",
    "RecommendationV2SeasonalityFilter",
    "RecommendationV2TravelDestinationFilter",
    "RegionFilterType",
    "SeasonCode",
    "TravelDestinationRegionField",
    "normalize_optional_cost_term",
    "serialize_travel_destination_filter",
]
