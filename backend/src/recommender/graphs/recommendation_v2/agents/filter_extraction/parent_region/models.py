from __future__ import annotations

from typing import Literal

from pydantic import BaseModel
from pydantic import Field


class ParentRegionEntry(BaseModel):
    """A single parent-region filter entry with include/exclude intent."""

    name: str = Field(
        ...,
        description="Parent-region name, must match an allowed parent_region value",
    )
    type: Literal["include", "exclude"] = Field(
        ...,
        description="Whether the user wants to include or exclude this parent-region",
    )


class RecommendationV2ParentRegionFilterExtractionInput(BaseModel):
    """Input payload for parent-region filter extraction from the current turn."""

    current_user_request: str = Field(
        ...,
        description="Raw user request from the current chat turn",
    )


class RecommendationV2ParentRegionFilterExtractionResult(BaseModel):
    """Structured parent_region filters extracted for recommendation_v2."""

    parent_regions: list[ParentRegionEntry] | None = Field(
        None,
        description="Parent-region filters mapped from the current user request with include/exclude intent",
    )
