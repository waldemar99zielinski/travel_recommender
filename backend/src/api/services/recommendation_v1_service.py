from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from api.schemas.recommendation import RecommendationRequestDto
from api.utils.sse import format_sse
from recommender.models.session.session import Session
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class RecommendationV1Service:
    def __init__(
        self,
        *,
        recommendation_graph: Any,
    ) -> None:
        self._recommendation_graph = recommendation_graph
        logger.info("Recommendation v1 service initialized")

    async def chat_stream(
        self,
        request: RecommendationRequestDto,
    ) -> AsyncGenerator[str, None]:
        session = Session(
            user_id=request.session.user_id,
            session_id=request.session.session_id,
        )
        logger.info(
            "Recommendation v1 streaming: user_id=%s, session_id=%s",
            session.user_id,
            session.session_id,
        )

        try:
            async for event_payload in self._recommendation_graph.astream(
                {
                    "session": session,
                    "user_request": request.message,
                },
                stream_mode="custom",
            ):
                if not isinstance(event_payload, dict):
                    logger.warning(
                        "Ignoring malformed recommendation stream payload: %r",
                        event_payload,
                    )
                    continue

                event_name = event_payload.get("event")
                event_data = event_payload.get("data", {})
                if not isinstance(event_name, str):
                    logger.warning(
                        "Ignoring recommendation stream payload without event name: %r",
                        event_payload,
                    )
                    continue

                yield format_sse(event_name, event_data)

            logger.info(
                "Recommendation v1 streaming completed: user_id=%s, session_id=%s",
                session.user_id,
                session.session_id,
            )

        except Exception:
            logger.exception(
                "Recommendation v1 streaming failed: user_id=%s, session_id=%s",
                request.session.user_id,
                request.session.session_id,
            )
            yield format_sse(
                "error",
                {"message": "An internal error occurred while generating recommendations."},
            )
