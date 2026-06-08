from __future__ import annotations

import json

MESSAGE_DELIMITER = "\n\n"


def format_sse(event: str, data: dict[str, object]) -> str:
    """Format an SSE event string.

    Args:
        event: The SSE event type name.
        data: The event payload as a dictionary (serialized to JSON).

    Returns:
        A string formatted as an SSE event frame.
    """
    return f"event: {event}\ndata: {json.dumps(data, default=str)}{MESSAGE_DELIMITER}"
