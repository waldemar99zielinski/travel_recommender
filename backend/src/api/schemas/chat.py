from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from pydantic import Field

from storage.models.chat_record import ChatRecord


class ChatTextMessageContextDto(BaseModel):
    text: str = Field(...)


class ChatMessageDto(BaseModel):
    type: str = Field(default="text")
    context: ChatTextMessageContextDto = Field(...)


def create_text_chat_message(text: str) -> ChatMessageDto:
    return ChatMessageDto(type="text", context=ChatTextMessageContextDto(text=text))

class ChatRecordDto(BaseModel):
    user_id: str = Field(...)
    session_id: str = Field(...)
    chat_history_number: int = Field(..., ge=0)
    user_request: str = Field(default="")
    system_response: str = Field(default="")
    recommendations: list[dict[str, Any]] = Field(default_factory=list)
    travel_destinations_evaluations: list[dict[str, Any]] = Field(default_factory=list)
    included_regions_ids: list[str] = Field(default_factory=list)
    excluded_regions_ids: list[str] = Field(default_factory=list)

    @classmethod
    def from_chat_record(cls, record: ChatRecord) -> ChatRecordDto:
        return cls(
            user_id=str(record.user_id),
            session_id=str(record.session_id),
            chat_history_number=record.chat_history_number,
            user_request=record.user_request,
            system_response=record.system_response,
            recommendations=record.recommendations,
            travel_destinations_evaluations=record.travel_destinations_evaluations,
            included_regions_ids=record.included_regions_ids,
            excluded_regions_ids=record.excluded_regions_ids,
        )
