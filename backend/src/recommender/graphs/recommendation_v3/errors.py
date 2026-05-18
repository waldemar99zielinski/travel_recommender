from __future__ import annotations


class RecommendationV3Error(Exception):
    """Base exception for recommendation_v3 graph errors."""


class RecommendationV3EmptyUserInputError(RecommendationV3Error, ValueError):
    """Raised when recommendation_v3 receives an empty user input."""

    def __init__(self) -> None:
        super().__init__("user_input must not be empty")


class RecommendationV3MissingQueryError(RecommendationV3Error, ValueError):
    """Raised when response generation is triggered without a synthesized query."""

    def __init__(self) -> None:
        super().__init__("synthesized_query must not be empty for run_new_recommendation outcome")
