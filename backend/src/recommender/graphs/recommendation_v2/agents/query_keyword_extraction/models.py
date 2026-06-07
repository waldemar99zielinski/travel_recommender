from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field


class RecommendationV2QueryKeywordExtractionInput(BaseModel):
    """Input payload for keyword extraction from a synthesized query."""

    synthesized_query: str = Field(
        ...,
        description="Interest-focused synthesized query to extract direct-search keywords from",
    )


class RecommendationV2QueryKeywordExtractionResult(BaseModel):
    """Structured keyword extraction result for a synthesized query."""

    keywords: list[str] = Field(
        default_factory=list,
        description="Concrete direct-search keywords extracted from the synthesized query",
    )
