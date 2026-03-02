from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field


class RecommendationMessageOutput(BaseModel):
    """Natural-language message generated for the final recommendation response."""

    message: str = Field(
        ...,
        description="Conversational user-facing message based on recommendation graph state",
    )
