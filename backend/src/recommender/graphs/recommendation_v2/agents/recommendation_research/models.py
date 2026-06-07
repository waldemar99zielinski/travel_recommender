from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field

from storage.models.chat_record import ChatRecord


class RecommendationV2RecommendationResearchInput(BaseModel):
    """Input payload for recommendation_v2 recommendation research."""

    region_name: str = Field(
        ...,
        description="Name of the region that should be researched",
    )
    region_description: str = Field(
        ...,
        description="Existing internal description of the region",
    )
    synthesized_user_query: str = Field(
        ...,
        description="History-aware synthesized user request that should shape the research",
    )
    conversation: list[ChatRecord] | None = Field(
        None,
        description="Persisted conversation history for the active session",
    )


class RecommendationV2RecommendationResearchResult(BaseModel):
    """Structured researched content for a single region."""

    description: str = Field(
        ...,
        description="Tailored description of what the user can do in the region",
    )
    image_urls: list[str] = Field(
        default_factory=list,
        description="Photo URLs that visually match the region and user request",
    )
