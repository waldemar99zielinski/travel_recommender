from __future__ import annotations

from typing import Any

from api.schemas.recommendation import RecommendationItemDto
from api.schemas.recommendation import RecommendationRequestDto
from api.schemas.recommendation import RecommendationResponseDto
from recommender.graphs.recommendation.models import RecommendationGraphState
from recommender.models.session.session import Session
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class RecommendationService:
    def __init__(
        self,
        *,
        recommendation_graph: Any,
    ) -> None:
        self._recommendation_graph = recommendation_graph
        logger.info("Real recommendation service initialized")

    def chat(self, request: RecommendationRequestDto) -> RecommendationResponseDto:
        logger.info(
            "Graph chat called: user_id=%s, session_id=%s",
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

        graph_state = RecommendationGraphState.model_validate(graph_result)
        recommendations = [
            RecommendationItemDto.from_recommendation(item)
            for item in (graph_state.recommendation or [])
        ]
        response = RecommendationResponseDto(
            message=graph_state.response if graph_state.response is not None else "",
            recommendations=recommendations,
        )
        logger.info(
            "Graph chat completed: user_id=%s, session_id=%s, status=%s",
            request.user_id,
            request.session_id,
            graph_state.status.value,
        )
        return response
