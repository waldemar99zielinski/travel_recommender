from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field


class Session(BaseModel):
    """Conversation scope identifiers for recommendation graph execution."""

    user_id: str = Field(..., description="User identifier owning the conversation")
    session_id: str = Field(..., description="Session/thread identifier for conversation memory")

    def __repr__(self) -> str:
        lines = ["Session("]
        lines.append(f"  user_id={self.user_id!r},")
        lines.append(f"  session_id={self.session_id!r},")
        lines.append(")")
        return "\n".join(lines)
