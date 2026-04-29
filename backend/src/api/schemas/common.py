from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from pydantic import Field


class ErrorResponseDto(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: dict[str, Any] | None = Field(
        ...,
        description="Optional contextual details",
    )
