from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from langgraph.config import get_stream_writer

from recommender.graphs.recommendation_v2.filter_models import (
    RecommendationV2TravelDestinationFilter,
)
from recommender.graphs.recommendation_v2.models import RecommendationV2
from recommender.models.session.session import Session
from storage.models.chat_record import ChatRecord


class EventType(StrEnum):
    INITIALIZING = "initializing"
    VALIDATING_REQUEST = "validating_request"
    GATHERING_FILTER = "gathering_filter"
    FILTER = "filter"
    RECOMMENDATION_GENERATION = "recommendation_generation"
    RECOMMENDATION = "recommendation"
    RESPONSE_GENERATION = "response_generation"
    RESPONSE = "response"
    DONE = "done"


@dataclass
class StreamEventResponseMessage:
    message: str

    def serialize(self) -> dict[str, object]:
        return {"message": self.message}


@dataclass
class StreamEventTravelDestinationFilter:
    travel_destination_filter: RecommendationV2TravelDestinationFilter

    def serialize(self) -> dict[str, object]:
        return self.travel_destination_filter.serialize()


@dataclass
class StreamEventRecommendation:
    recommendations: list[RecommendationV2]

    def serialize(self) -> dict[str, object]:
        return {
            "recommendations": [
                recommendation.serialize() for recommendation in self.recommendations
            ],
        }


@dataclass
class StreamEventChatRecord:
    chat_record: ChatRecord

    def serialize(self) -> dict[str, object]:
        return {
            "user_id": str(self.chat_record.user_id) if self.chat_record.user_id else None,
            "session_id": str(self.chat_record.session_id) if self.chat_record.session_id else None,
            "chat_history_number": self.chat_record.chat_history_number,
            "user_request": self.chat_record.user_request,
            "system_response": self.chat_record.system_response,
            "synthesized_query": self.chat_record.synthesized_query,
            "recommendations": self.chat_record.recommendations,
            "travel_destinations_evaluations": self.chat_record.travel_destinations_evaluations,
            "graph_version": self.chat_record.graph_version,
            "message_type": self.chat_record.message_type,
        }


def emit_stream_event(event: EventType, data: dict[str, object]) -> None:
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
