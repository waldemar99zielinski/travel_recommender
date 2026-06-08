from __future__ import annotations

from enum import Enum
from typing import Annotated
from typing import Literal
from typing import TypeAlias
from typing import Union

from pydantic import BaseModel
from pydantic import Field


class RecommendationStreamMessageType(str, Enum):
    """Identifies the intended message flow for a streaming recommendation request."""

    USER_MESSAGE = "user_message"
    EXPLORE_DESTINATION = "explore_destination"


class ExploreDestinationPayload(BaseModel):
    """Payload for an explore_destination message — carries the destination to explore."""

    destination_id: str = Field(..., min_length=1, description="ID of the travel destination to explore")


class ExploreDestinationRequestDto(BaseModel):
    """Stream request for the Explore Destination intent."""

    request_type: Literal[RecommendationStreamMessageType.EXPLORE_DESTINATION] = Field(
        ..., description="Discriminator for the message payload"
    )
    user_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., description="Raw user message text")
    data: ExploreDestinationPayload = Field(..., description="Additional payload for explore_destination requests")


class UserMessageRequestDto(BaseModel):
    """Stream request for a raw free-form user message."""

    request_type: Literal[RecommendationStreamMessageType.USER_MESSAGE] = Field(
        ..., description="Discriminator for the message payload"
    )
    user_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., description="Raw user message text")


RecommendationStreamRequestDto: TypeAlias = Annotated[
    Union[ExploreDestinationRequestDto, UserMessageRequestDto],
    Field(discriminator="request_type"),
]


class RecommendationStreamEventDto(BaseModel):
    event: str = Field(..., description="Event type identifying the payload shape")
    data: dict = Field(default_factory=dict, description="Event payload, schema depends on event type")
