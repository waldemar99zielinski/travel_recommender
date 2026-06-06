from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field

from storage.models.chat_record import ChatRecord


class RecommendationV2OutOfScopeResponseGenerationInput(BaseModel):
    """Input payload for out-of-scope recommendation_v2 responses."""

    current_user_request: str = Field(
        ...,
        description="Raw user request from the current chat turn",
    )
    chat_history: list[ChatRecord] | None = Field(
        None,
        description="Persisted chat history for the active session",
    )
