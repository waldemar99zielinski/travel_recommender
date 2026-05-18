from __future__ import annotations

from typing import Any

from api.schemas.chat_message import create_text_chat_message
from api.schemas.recommendation import RecommendationItemDto
from api.schemas.recommendation import RecommendationRequestDto
from api.schemas.recommendation import RecommendationResponseDto
from recommender.graphs.recommendation_v2.models import RecommendationV2GraphState
from recommender.models.session.session import Session
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class RecommendationV2Service:
    """Service wrapper for the recommendation_v2 graph."""

    def __init__(
        self,
        *,
        recommendation_graph: Any,
    ) -> None:
        self._recommendation_graph = recommendation_graph
        logger.info("Recommendation v2 service initialized")

    def chat(self, request: RecommendationRequestDto) -> RecommendationResponseDto:
        logger.info(
            "Recommendation v2 graph chat called: user_id=%s, session_id=%s",
            request.user_id,
            request.session_id,
        )

        session = Session(user_id=request.user_id, session_id=request.session_id)
        graph_result = self._recommendation_graph.invoke(
            {
                "session": session,
                "user_input": request.message,
            },
        )

        graph_state = RecommendationV2GraphState.model_validate(graph_result)
        recommendations = [
            RecommendationItemDto.from_recommendation(item)
            for item in (graph_state.recommendation or [])
        ]
        response = RecommendationResponseDto(
            messages=(
                [create_text_chat_message(graph_state.response)]
                if graph_state.response is not None and graph_state.response.strip()
                else []
            ),
            recommendations=recommendations,
        )
        logger.info(
            "Recommendation v2 graph chat completed: user_id=%s, session_id=%s, status=%s",
            request.user_id,
            request.session_id,
            graph_state.status.value,
        )
        return response
