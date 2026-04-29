from __future__ import annotations

from uuid import uuid4

from api.core.exceptions import SessionNotFoundError
from api.schemas.session import SessionCreateRequestDto
from api.schemas.session import SessionCreateResponseDto
from api.schemas.session import SessionDeleteResponseDto
from api.schemas.session import SessionRefDto
from api.schemas.session import SessionStateResponseDto
from storage.stores.contracts import RecommendationSessionStoreProtocol
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class SessionService:
    """Service for recommendation session lifecycle operations."""

    def __init__(self, *, recommendation_session_store: RecommendationSessionStoreProtocol) -> None:
        self._recommendation_session_store = recommendation_session_store
        logger.info("Session service initialized")

    def create_session(
        self,
        request: SessionCreateRequestDto | None = None,
    ) -> SessionCreateResponseDto:
        user_id = request.user_id.strip() if request is not None and request.user_id is not None else ""
        if user_id == "":
            user_id = str(uuid4())

        session_ref = SessionRefDto(user_id=user_id, session_id=str(uuid4()))

        logger.info(
            "Session created: user_id=%s, session_id=%s",
            session_ref.user_id,
            session_ref.session_id,
        )

        return SessionCreateResponseDto(session=session_ref)

    def get_session(self, session: SessionRefDto) -> SessionStateResponseDto:
        rows = self._recommendation_session_store.load_session(
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
        return SessionStateResponseDto(session=session)

    def delete_session(self, session: SessionRefDto) -> SessionDeleteResponseDto:
        rows = self._recommendation_session_store.load_session(
            user_id=session.user_id,
            session_id=session.session_id,
        )
        deleted = len(rows) > 0
        if deleted:
            self._recommendation_session_store.delete_session(
                user_id=session.user_id,
                session_id=session.session_id,
            )

        logger.info(
            "Session delete request completed: user_id=%s, session_id=%s, deleted=%s",
            session.user_id,
            session.session_id,
            deleted,
        )
        return SessionDeleteResponseDto(session=session)
