from __future__ import annotations

from typing import Literal

from pydantic import BaseModel
from pydantic import Field


class DirectRegionEntry(BaseModel):
    """A single direct-region filter entry with include/exclude intent."""

    name: str = Field(
        ...,
        description="Direct region name, must match an allowed direct region value",
    )
    type: Literal["include", "exclude"] = Field(
        ...,
        description="Whether the user wants to include or exclude this region",
    )


class RecommendationV2DirectRegionFilterExtractionInput(BaseModel):
    """Input payload for direct-region filter extraction from the current turn."""

    current_user_request: str = Field(
        ...,
        description="Raw user request from the current chat turn",
    )

class RecommendationV2DirectRegionFilterExtractionResult(BaseModel):
    """Structured direct-region filters extracted for recommendation_v2."""

    regions: list[DirectRegionEntry] | None = Field(
        None,
        description="Direct region filters mapped from the current user request with include/exclude intent",
    )
