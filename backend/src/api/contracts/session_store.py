from __future__ import annotations

from typing import Protocol


class SessionStoreProtocol(Protocol):
    def get_history(self, *, user_id: str, session_id: str) -> list[str] | None:
        ...

    def append_message(self, *, user_id: str, session_id: str, message: str) -> None:
        ...

    def delete(self, *, user_id: str, session_id: str) -> bool:
        ...
