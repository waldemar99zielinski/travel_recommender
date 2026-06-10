from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import ClassVar, Literal, TypeAlias

from pydantic import BaseModel
from pydantic import Field
from pydantic import model_validator

from storage.models.travel_destination import TravelDestinationRecord

TravelDestinationTextField: TypeAlias = Literal[
    "id",
    "parent_region",
    "region",
    "description",
]

TravelDestinationNumericField: TypeAlias = Literal[
    "popularity",
    "cost_per_week",
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
    "embedding_version",
]

TravelDestinationDatetimeField: TypeAlias = Literal[
    "created_at",
    "updated_at",
]

TravelDestinationFilterField: TypeAlias = (
    TravelDestinationTextField
    | TravelDestinationNumericField
    | TravelDestinationDatetimeField
)

TravelDestinationQueryOperator: TypeAlias = Literal[
    "eq",
    "ne",
    "gt",
    "gte",
    "lt",
    "lte",
    "between",
    "in",
    "starts_with",
    "like",
    "ilike",
]

TravelDestinationSortField: TypeAlias = TravelDestinationFilterField
TravelDestinationSortDirection: TypeAlias = Literal["asc", "desc"]
PrimitiveQueryValue: TypeAlias = str | int | float | bool

MAX_QUERY_FILTERS = 12
MAX_QUERY_SORTS = 4
MAX_FILTER_VALUES = 25
MAX_TEXT_QUERY_LENGTH = 240
MAX_SEMANTIC_QUERY_LENGTH = 500
MAX_FILTER_TEXT_LENGTH = 120

TEXT_FIELDS: tuple[TravelDestinationTextField, ...] = (
    "id",
    "parent_region",
    "region",
    "description",
)
NUMERIC_FIELDS: tuple[TravelDestinationNumericField, ...] = (
    "popularity",
    "cost_per_week",
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
    "embedding_version",
)
DATETIME_FIELDS: tuple[TravelDestinationDatetimeField, ...] = (
    "created_at",
    "updated_at",
)
DEFAULT_TEXT_FIELDS: tuple[TravelDestinationTextField, ...] = (
    "region",
    "parent_region",
    "description",
)


class TravelDestinationQueryFilter(BaseModel):
    """One validated structured predicate for destination querying."""

    _VALUE_OPERATORS: ClassVar[set[str]] = {"eq", "ne", "gt", "gte", "lt", "lte", "starts_with", "like", "ilike"}
    _VALUES_OPERATORS: ClassVar[set[str]] = {"in"}
    _RANGE_OPERATORS: ClassVar[set[str]] = {"between"}
    _TEXT_ONLY_OPERATORS: ClassVar[set[str]] = {"starts_with", "like", "ilike"}

    field: TravelDestinationFilterField
    operator: TravelDestinationQueryOperator
    value: PrimitiveQueryValue | None = None
    values: tuple[PrimitiveQueryValue, ...] = Field(default_factory=tuple)
    min_value: PrimitiveQueryValue | None = None
    max_value: PrimitiveQueryValue | None = None

    @model_validator(mode="after")
    def validate_shape(self) -> TravelDestinationQueryFilter:
        if self.operator in self._VALUE_OPERATORS and self.value is None:
            raise ValueError(f"operator '{self.operator}' requires value")

        if self.operator in self._VALUES_OPERATORS and not self.values:
            raise ValueError(f"operator '{self.operator}' requires values")

        if self.operator in self._RANGE_OPERATORS and (self.min_value is None or self.max_value is None):
            raise ValueError("operator 'between' requires min_value and max_value")

        if self.operator in self._TEXT_ONLY_OPERATORS and self.field not in TEXT_FIELDS:
            raise ValueError(f"operator '{self.operator}' is only supported for text fields")

        if self.operator in {"gt", "gte", "lt", "lte", "between"} and self.field in TEXT_FIELDS:
            raise ValueError(f"operator '{self.operator}' is not supported for text fields")

        if len(self.values) > MAX_FILTER_VALUES:
            raise ValueError(f"operator '{self.operator}' supports at most {MAX_FILTER_VALUES} values")

        self._validate_primitive_value(self.value, context=f"filter '{self.field}'", field=self.field)
        self._validate_primitive_value(self.min_value, context=f"filter '{self.field}'", field=self.field)
        self._validate_primitive_value(self.max_value, context=f"filter '{self.field}'", field=self.field)
        for entry in self.values:
            self._validate_primitive_value(entry, context=f"filter '{self.field}'", field=self.field)

        if self.operator in {"like", "ilike"} and self.value is not None:
            pattern = self._require_string_value(self.value, context=f"filter '{self.field}'")
            if pattern.lstrip().startswith(("%", "_")):
                raise ValueError(f"operator '{self.operator}' does not allow leading wildcards")
            if all(character in {"%", "_"} for character in pattern):
                raise ValueError(f"operator '{self.operator}' does not allow wildcard-only patterns")

        return self

    @staticmethod
    def _validate_primitive_value(
        value: PrimitiveQueryValue | None,
        *,
        context: str,
        field: TravelDestinationFilterField,
    ) -> None:
        if value is None or isinstance(value, bool):
            return
        if isinstance(value, str):
            if len(value.strip()) > MAX_FILTER_TEXT_LENGTH:
                raise ValueError(f"{context} text values must be at most {MAX_FILTER_TEXT_LENGTH} characters")
            if field in NUMERIC_FIELDS:
                TravelDestinationQueryFilter._validate_numeric_string(value, context=context, field=field)
            return
        if not isfinite(float(value)):
            raise ValueError(f"{context} numeric values must be finite")

    @staticmethod
    def _validate_numeric_string(value: str, *, context: str, field: TravelDestinationFilterField) -> None:
        normalized = value.strip()
        try:
            parsed = int(normalized) if field == "embedding_version" else float(normalized)
        except ValueError as error:
            raise ValueError(f"{context} requires numeric values") from error
        if not isfinite(float(parsed)):
            raise ValueError(f"{context} numeric values must be finite")

    @staticmethod
    def _require_string_value(value: PrimitiveQueryValue, *, context: str) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{context} requires string values")
        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{context} requires non-empty string values")
        return normalized


class TravelDestinationQuerySort(BaseModel):
    """Sort instruction for structured destination queries."""

    field: TravelDestinationSortField
    direction: TravelDestinationSortDirection = "asc"


class TravelDestinationQuery(BaseModel):
    """Validated query request suitable for tool-calling and storage lookups."""

    filters: tuple[TravelDestinationQueryFilter, ...] = Field(default_factory=tuple)
    text_query: str | None = None
    text_fields: tuple[TravelDestinationTextField, ...] = Field(default_factory=lambda: DEFAULT_TEXT_FIELDS)
    semantic_query: str | None = None
    semantic_weight: float = Field(default=0.7, ge=0.0)
    text_weight: float = Field(default=0.3, ge=0.0)
    sort: tuple[TravelDestinationQuerySort, ...] = Field(default_factory=tuple)
    limit: int | None = Field(default=10, ge=1, le=100)

    @model_validator(mode="after")
    def validate_query(self) -> TravelDestinationQuery:
        normalized_text_query = self.text_query.strip() if self.text_query is not None else None
        self.text_query = normalized_text_query or None

        normalized_semantic_query = self.semantic_query.strip() if self.semantic_query is not None else None
        self.semantic_query = normalized_semantic_query or None

        normalized_text_fields: list[TravelDestinationTextField] = []
        for field in self.text_fields:
            if field not in normalized_text_fields:
                normalized_text_fields.append(field)
        self.text_fields = tuple(normalized_text_fields) or DEFAULT_TEXT_FIELDS

        if not self.filters and self.text_query is None and self.semantic_query is None:
            raise ValueError("query must define at least one filter, text_query, or semantic_query")

        if self.text_query is None and self.text_fields != DEFAULT_TEXT_FIELDS:
            raise ValueError("text_fields can only be set when text_query is provided")

        if self.text_query is not None and not self.text_fields:
            raise ValueError("text_query requires at least one text field")

        if self.text_query is not None and self.semantic_query is not None:
            if self.semantic_weight == 0.0 and self.text_weight == 0.0:
                raise ValueError("semantic_weight and text_weight cannot both be zero")

        if len(self.filters) > MAX_QUERY_FILTERS:
            raise ValueError(f"query supports at most {MAX_QUERY_FILTERS} filters")

        if len(self.sort) > MAX_QUERY_SORTS:
            raise ValueError(f"query supports at most {MAX_QUERY_SORTS} sort clauses")

        if self.text_query is not None and len(self.text_query) > MAX_TEXT_QUERY_LENGTH:
            raise ValueError(f"text_query must be at most {MAX_TEXT_QUERY_LENGTH} characters")

        if self.semantic_query is not None and len(self.semantic_query) > MAX_SEMANTIC_QUERY_LENGTH:
            raise ValueError(f"semantic_query must be at most {MAX_SEMANTIC_QUERY_LENGTH} characters")

        if not isfinite(self.semantic_weight):
            raise ValueError("semantic_weight must be finite")

        if not isfinite(self.text_weight):
            raise ValueError("text_weight must be finite")

        return self


@dataclass(frozen=True, slots=True)
class QueriedTravelDestination:
    """Structured query result with explicit text and semantic scores."""

    destination: TravelDestinationRecord
    embedding_distance: float
    semantic_score: float
    text_score: float
    ranking_score: float


def coerce_query_datetime(value: object) -> datetime:
    """Parse a supported query value into a datetime instance."""

    if isinstance(value, bool):
        raise ValueError("boolean values are not valid datetimes")
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        raise ValueError("datetime filters require ISO-8601 strings")

    normalized_value = value.strip()
    if not normalized_value:
        raise ValueError("datetime filters require non-empty ISO-8601 strings")

    if normalized_value.endswith("Z"):
        normalized_value = normalized_value[:-1] + "+00:00"
    return datetime.fromisoformat(normalized_value)
