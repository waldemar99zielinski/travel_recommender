from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends

from api.contracts.recommendation_service import RecommendationServiceProtocol
from api.dependencies import get_recommendation_v2_service
from api.schemas.recommendation import RecommendationRequestDto
from api.schemas.recommendation import RecommendationResponseDto
from utils.logger import LoggerManager

router = APIRouter(prefix="/api/v2/recommendations")
logger = LoggerManager.get_logger(__name__)


@router.post("/chat", response_model=RecommendationResponseDto)
def chat(
    payload: RecommendationRequestDto,
    service: RecommendationServiceProtocol = Depends(get_recommendation_v2_service),
) -> RecommendationResponseDto:
    logger.info(
        "Recommendation v2 chat request: user_id=%s, session_id=%s",
        payload.user_id,
        payload.session_id,
    )

    response = service.chat(payload)

    logger.info(
        "Recommendation v2 chat response generated successfully: user_id=%s, session_id=%s",
        payload.user_id,
        payload.session_id,
    )

    return response
