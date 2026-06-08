from __future__ import annotations

from uuid import uuid4

from api.core.exceptions import SessionNotFoundError
from api.schemas.session import ChatRecordDto
from api.schemas.session import SessionCreateRequestDto
from api.schemas.session import SessionCreateResponseDto
from api.schemas.session import SessionDeleteResponseDto
from api.schemas.session import SessionGetRequestDto
from api.schemas.session import SessionRefDto
from api.schemas.session import SessionStateResponseDto
from storage.stores.contracts import ChatStoreProtocol
from storage.stores.contracts import TravelDestinationStoreProtocol
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class SessionService:
    """Service for recommendation session lifecycle operations."""

    def __init__(
        self,
        *,
        chat_store: ChatStoreProtocol,
        travel_destination_store: TravelDestinationStoreProtocol,
    ) -> None:
        self._chat_store = chat_store
        self._travel_destination_store = travel_destination_store
        logger.info("Session service initialized")

    def create_session(
        self,
        request: SessionCreateRequestDto | None = None,
    ) -> SessionCreateResponseDto:
        user_id = request.user_id.strip() if request is not None and request.user_id is not None else ""
        if user_id == "":
            user_id = str(uuid4())

        session_ref = SessionRefDto(user_id=user_id, session_id=str(uuid4()), version="v2")

        logger.info(
            "Session created: user_id=%s, session_id=%s",
            session_ref.user_id,
            session_ref.session_id,
        )

        return SessionCreateResponseDto(session=session_ref)

    def get_session(self, session: SessionGetRequestDto) -> SessionStateResponseDto:
        rows = self._chat_store.load_session(
            user_id=session.user_id,
            session_id=session.session_id,
        )
        if not rows:
            raise SessionNotFoundError(user_id=session.user_id, session_id=session.session_id)

        logger.info(
            "Session loaded: user_id=%s, session_id=%s, rows=%d",
            session.user_id,
            session.session_id,
            len(rows),
        )

        chat_records_dto = [ChatRecordDto.from_chat_record(row) for row in rows] if rows else None
        session_ref = SessionRefDto(
            user_id=session.user_id,
            session_id=session.session_id,
            version=rows[0].graph_version,
        )

        return SessionStateResponseDto(
            session=session_ref,
            chat_history=chat_records_dto,
        )

    def delete_session(self, session: SessionGetRequestDto) -> SessionDeleteResponseDto:
        rows = self._chat_store.load_session(
            user_id=session.user_id,
            session_id=session.session_id,
        )
        deleted = len(rows) > 0
        session_ref = SessionRefDto(
            user_id=session.user_id,
            session_id=session.session_id,
            version=rows[0].graph_version if deleted else "v1",
        )
        if deleted:
            self._chat_store.delete_session(
                user_id=session.user_id,
                session_id=session.session_id,
            )

        logger.info(
            "Session delete request completed: user_id=%s, session_id=%s, deleted=%s",
            session.user_id,
            session.session_id,
            deleted,
        )
        return SessionDeleteResponseDto(session=session_ref)
