from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

PREFERENCE_VALUE_MAP: dict[str, float] = {
    "--": 0.0,
    "-": 0.25,
    "o": 0.5,
    "+": 0.75,
    "++": 1.0,
}

PREFERENCE_FIELDS: tuple[str, ...] = (
    "popularity",
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
    "safety",
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

class TravelDestination(BaseModel):
    """Structured destination record loaded from travel CSV datasets."""

    def __init__(self, **data: Any) -> None:
        converted: dict[str, Any] = dict(data)
        for field_name in PREFERENCE_FIELDS:
            converted[field_name] = self._to_preference_level(converted.get(field_name))
        super().__init__(**converted)

    parent_region: str = Field(..., description="Parent region")
    region: str = Field(..., description="Destination region")
    u_name: str = Field(..., description="Display name from dataset")

    popularity: float = Field(..., ge=0, le=1, description="Popularity score in range [0, 1]")
    cost_per_week: float = Field(..., ge=0, description="Weekly travel cost")

    jan: float = Field(..., ge=0, le=1, description="Travel season score for January in range [0, 1]")
    feb: float = Field(..., ge=0, le=1, description="Travel season score for February in range [0, 1]")
    mar: float = Field(..., ge=0, le=1, description="Travel season score for March in range [0, 1]")
    apr: float = Field(..., ge=0, le=1, description="Travel season score for April in range [0, 1]")
    may: float = Field(..., ge=0, le=1, description="Travel season score for May in range [0, 1]")
    jun: float = Field(..., ge=0, le=1, description="Travel season score for June in range [0, 1]")
    jul: float = Field(..., ge=0, le=1, description="Travel season score for July in range [0, 1]")
    aug: float = Field(..., ge=0, le=1, description="Travel season score for August in range [0, 1]")
    sep: float = Field(..., ge=0, le=1, description="Travel season score for September in range [0, 1]")
    oct: float = Field(..., ge=0, le=1, description="Travel season score for October in range [0, 1]")
    nov: float = Field(..., ge=0, le=1, description="Travel season score for November in range [0, 1]")
    dec: float = Field(..., ge=0, le=1, description="Travel season score for December in range [0, 1]")

    safety: float = Field(..., ge=0, le=1, description="Safety preference score in range [0, 1]")
    nature: float = Field(..., ge=0, le=1, description="Nature preference score in range [0, 1]")
    hiking: float = Field(..., ge=0, le=1, description="Hiking preference score in range [0, 1]")
    beach: float = Field(..., ge=0, le=1, description="Beach preference score in range [0, 1]")
    watersports: float = Field(..., ge=0, le=1, description="Watersports preference score in range [0, 1]")
    entertainment: float = Field(..., ge=0, le=1, description="Entertainment preference score in range [0, 1]")
    wintersports: float = Field(..., ge=0, le=1, description="Wintersports preference score in range [0, 1]")
    culture: float = Field(..., ge=0, le=1, description="Culture preference score in range [0, 1]")
    culinary: float = Field(..., ge=0, le=1, description="Culinary preference score in range [0, 1]")
    architecture: float = Field(..., ge=0, le=1, description="Architecture preference score in range [0, 1]")
    shopping: float = Field(..., ge=0, le=1, description="Shopping preference score in range [0, 1]")

    description: str = Field(..., description="Destination description")

    def _to_preference_level(self, value: Any) -> float | None:
        if value is None:
            return None

        if isinstance(value, (int, float)):
            numeric_value = float(value)
            if 0.0 <= numeric_value <= 1.0:
                return numeric_value
            return None

        normalized = str(value).strip()
        if not normalized:
            return None

        return PREFERENCE_VALUE_MAP.get(normalized)
