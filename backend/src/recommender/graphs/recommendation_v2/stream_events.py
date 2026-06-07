from __future__ import annotations

from langgraph.config import get_stream_writer

from recommender.graphs.recommendation_v2.models import RecommendationV2
from recommender.models.session.session import Session


def emit_stream_event(event: str, data: dict[str, object]) -> None:
    try:
        stream_writer = get_stream_writer()
    except Exception:
        return

    stream_writer({"event": event, "data": data})


def build_recommendation_event_payload(
    *,
    session: Session,
    user_request: str,
    system_response: str,
    recommendations: list[RecommendationV2] | None,
    chat_history_number: int,
) -> dict[str, object]:
    return {
        "user_id": session.user_id,
        "session_id": session.session_id,
        "chat_history_number": chat_history_number,
        "user_request": user_request,
        "system_response": system_response,
        "recommendations": [
            recommendation.serialize() for recommendation in recommendations or []
        ],
        "travel_destinations_evaluations": [],
    }
