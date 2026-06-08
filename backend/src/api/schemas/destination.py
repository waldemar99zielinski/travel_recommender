from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field

from storage.models.travel_destination import TravelDestinationRecord


class DestinationItemDto(BaseModel):
    """Public representation of a travel destination with id and description."""

    id: str = Field(..., description="Unique destination identifier")
    description: str = Field(..., description="Destination description text")

    @classmethod
    def from_record(cls, record: TravelDestinationRecord) -> DestinationItemDto:
        return cls(
            id=record.id,
            description=record.description,
        )


class DestinationListResponseDto(BaseModel):
    """Response wrapping a list of travel destinations."""

    destinations: list[DestinationItemDto] = Field(
        default_factory=list,
        description="List of all travel destinations",
    )
    total: int = Field(..., description="Total number of destinations")
