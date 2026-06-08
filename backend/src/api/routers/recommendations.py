from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import StreamingResponse

from api.dependencies import get_recommendation_v1_service
from api.schemas.recommendation import RecommendationRequestDto
from utils.logger import LoggerManager

router = APIRouter(prefix="/api/v1/recommendations")
logger = LoggerManager.get_logger(__name__)


@router.post("/chat")
async def chat_stream(
    payload: RecommendationRequestDto,
    service: Any = Depends(get_recommendation_v1_service),
):
    logger.info(
        "Recommendation v1 chat streaming request: user_id=%s, session_id=%s",
        payload.session.user_id,
        payload.session.session_id,
    )

    return StreamingResponse(
        service.chat_stream(payload),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
