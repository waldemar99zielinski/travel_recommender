from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator

from recommender.graphs.recommendation_v2.filter_models import CostTerm
from recommender.graphs.recommendation_v2.filter_models import normalize_optional_cost_term


class RecommendationV2BudgetFilterExtractionInput(BaseModel):
    """Input payload for recommendation_v2 budget-filter extraction."""

    current_user_request: str = Field(
        ...,
        description="Raw user request from the current chat turn",
    )
    previous_cost_term: CostTerm | None = Field(
        None,
        description="Previously extracted budget term for this session",
    )


class RecommendationV2BudgetFilterExtractionResult(BaseModel):
    """Structured budget filters extracted for recommendation_v2."""

    filter_removed: bool = Field(
        False,
        description="Whether the user explicitly requested removal of the budget filter category.",
    )

    cost_term: CostTerm | None = Field(
        None,
        description="Updated budget term after applying the current user request",
    )

    @field_validator("cost_term", mode="before")
    @classmethod
    def normalize_empty_cost_term(cls, value: object) -> object:
        return normalize_optional_cost_term(value)
