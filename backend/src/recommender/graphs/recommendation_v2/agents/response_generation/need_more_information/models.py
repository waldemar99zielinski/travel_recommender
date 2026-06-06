from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field

from storage.models.chat_record import ChatRecord


class RecommendationV2NeedMoreInformationResponseGenerationInput(BaseModel):
    """Input payload for recommendation_v2 responses that ask for more detail."""

    current_user_request: str = Field(
        ...,
        description="Raw user request from the current chat turn",
    )
    chat_history: list[ChatRecord] | None = Field(
        None,
        description="Persisted chat history for the active session",
    )
