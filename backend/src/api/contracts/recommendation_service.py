from __future__ import annotations

from typing import Protocol

from api.schemas.recommendation import RecommendationRequestDto
from api.schemas.recommendation import RecommendationResponseDto

class RecommendationServiceProtocol(Protocol):
    def chat(self, request: RecommendationRequestDto) -> RecommendationResponseDto:
        ...
