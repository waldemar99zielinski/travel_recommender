from __future__ import annotations

from typing import Protocol

from api.schemas.session import SessionCreateRequestDto
from api.schemas.session import SessionCreateResponseDto
from api.schemas.session import SessionDeleteResponseDto
from api.schemas.session import SessionRefDto
from api.schemas.session import SessionStateResponseDto


class SessionServiceProtocol(Protocol):
    def create_session(
        self,
        request: SessionCreateRequestDto | None = None,
    ) -> SessionCreateResponseDto:
        ...

    def get_session(self, session: SessionRefDto) -> SessionStateResponseDto:
        ...

    def delete_session(self, session: SessionRefDto) -> SessionDeleteResponseDto:
        ...
