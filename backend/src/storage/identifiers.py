from __future__ import annotations

from uuid import NAMESPACE_URL
from uuid import UUID
from uuid import uuid5


def normalize_identifier_to_uuid(value: UUID | str, *, field_name: str) -> UUID:
    """Return a stable UUID for persisted storage identifiers.

    Accepts native UUID values, UUID-formatted strings, or arbitrary non-empty strings.
    Non-UUID strings are mapped to a deterministic UUID5 so API callers are not forced to
    provide UUIDs as long as they use stable identifier values.
    """

    if isinstance(value, UUID):
        return value

    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")

    try:
        return UUID(normalized)
    except ValueError:
        return uuid5(NAMESPACE_URL, f"hybrid:{field_name}:{normalized}")
