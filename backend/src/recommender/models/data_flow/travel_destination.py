from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel
from pydantic import Field

NormalizedPreference = Annotated[
    float,
    Field(
        ge=0.0,
        le=1.0,
        multiple_of=0.25,
        strict=True,
    ),
]


class TravelDestination(BaseModel):
    """Structured travel destination with required fields."""

    parent_region: str = Field(..., description="Parent region")
    region: str = Field(..., description="Destination region")
    u_name: str = Field(..., description="Display name from dataset")

    popularity: NormalizedPreference = Field(
        ...,
        description="Popularity score normalized to [0, 1] with step 0.25",
    )
    cost_per_week: float = Field(..., description="Weekly travel cost")

    jan: NormalizedPreference = Field(..., description="Travel season score for January in [0, 1] with step 0.25")
    feb: NormalizedPreference = Field(..., description="Travel season score for February in [0, 1] with step 0.25")
    mar: NormalizedPreference = Field(..., description="Travel season score for March in [0, 1] with step 0.25")
    apr: NormalizedPreference = Field(..., description="Travel season score for April in [0, 1] with step 0.25")
    may: NormalizedPreference = Field(..., description="Travel season score for May in [0, 1] with step 0.25")
    jun: NormalizedPreference = Field(..., description="Travel season score for June in [0, 1] with step 0.25")
    jul: NormalizedPreference = Field(..., description="Travel season score for July in [0, 1] with step 0.25")
    aug: NormalizedPreference = Field(..., description="Travel season score for August in [0, 1] with step 0.25")
    sep: NormalizedPreference = Field(..., description="Travel season score for September in [0, 1] with step 0.25")
    oct: NormalizedPreference = Field(..., description="Travel season score for October in [0, 1] with step 0.25")
    nov: NormalizedPreference = Field(..., description="Travel season score for November in [0, 1] with step 0.25")
    dec: NormalizedPreference = Field(..., description="Travel season score for December in [0, 1] with step 0.25")

    # safety: NormalizedPreference = Field(..., description="Safety preference score in [0, 1] with step 0.25")
    nature: NormalizedPreference = Field(..., description="Nature preference score in [0, 1] with step 0.25")
    hiking: NormalizedPreference = Field(..., description="Hiking preference score in [0, 1] with step 0.25")
    beach: NormalizedPreference = Field(..., description="Beach preference score in [0, 1] with step 0.25")
    watersports: NormalizedPreference = Field(..., description="Watersports preference score in [0, 1] with step 0.25")
    entertainment: NormalizedPreference = Field(..., description="Entertainment preference score in [0, 1] with step 0.25")
    wintersports: NormalizedPreference = Field(..., description="Wintersports preference score in [0, 1] with step 0.25")
    culture: NormalizedPreference = Field(..., description="Culture preference score in [0, 1] with step 0.25")
    culinary: NormalizedPreference = Field(..., description="Culinary preference score in [0, 1] with step 0.25")
    architecture: NormalizedPreference = Field(..., description="Architecture preference score in [0, 1] with step 0.25")
    shopping: NormalizedPreference = Field(..., description="Shopping preference score in [0, 1] with step 0.25")

    description: str = Field(..., description="Destination description")

    def __repr__(self) -> str:
        lines: list[str] = ["TravelDestination("]
        lines.append(f"  region={self.region!r},")
        lines.append(f"  parent_region={self.parent_region!r},")
        lines.append(f"  u_name={self.u_name!r},")
        lines.append(f"  popularity={self.popularity!r},")
        lines.append(f"  cost_per_week={self.cost_per_week!r},")
        lines.append(")")
        return "\n".join(lines)
