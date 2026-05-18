from __future__ import annotations

from enum import Enum
from typing import Annotated
from typing import Literal
from typing import TypeAlias

from pydantic import BaseModel
from pydantic import Field
from pydantic import TypeAdapter


class ChatMessageTypeEnum(str, Enum):
    """Supported assistant chat message types."""

    TEXT = "text"


class ChatMessageContextDto(BaseModel):
    """Base type for chat message context payloads."""


class ChatTextMessageContextDto(ChatMessageContextDto):
    """Typed context payload for plain text assistant chat messages."""

    text: str = Field(..., description="Text content displayed to the user")


class ChatTextMessageDto(BaseModel):
    """Structured plain-text assistant chat message."""

    type: Literal[ChatMessageTypeEnum.TEXT] = Field(
        ..., description="Discriminator for the message payload"
    )
    context: ChatTextMessageContextDto = Field(
        ..., description="Message payload for the selected type"
    )


ChatMessageDto: TypeAlias = Annotated[
    ChatTextMessageDto,
    Field(discriminator="type"),
]

_chat_message_adapter = TypeAdapter(ChatMessageDto)


def validate_chat_message(payload: object) -> ChatMessageDto:
    """Validate one structured chat message payload."""

    return _chat_message_adapter.validate_python(payload)


def create_text_chat_message(text: str) -> ChatMessageDto:
    """Build a structured text chat message from plain text."""

    return ChatTextMessageDto(
        type=ChatMessageTypeEnum.TEXT,
        context=ChatTextMessageContextDto(text=text),
    )
