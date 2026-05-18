from __future__ import annotations

from uuid import uuid4

from api.core.exceptions import SessionNotFoundError
from api.schemas.chat_message import ChatMessageDto
from api.schemas.chat_message import create_text_chat_message
from api.schemas.chat_message import validate_chat_message
from api.schemas.recommendation import RecommendationItemDto
from api.schemas.session import SessionCreateRequestDto
from api.schemas.session import SessionCreateResponseDto
from api.schemas.session import SessionDeleteResponseDto
from api.schemas.session import SessionHistoryTurnDto
from api.schemas.session import SessionRefDto
from api.schemas.session import SessionStateResponseDto
from storage.models.travel_destination import TravelDestinationRecord
from storage.stores.contracts import RecommendationSessionStoreProtocol
from storage.stores.contracts import TravelDestinationStoreProtocol
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class SessionService:
    """Service for recommendation session lifecycle operations."""

    def __init__(
        self,
        *,
        recommendation_session_store: RecommendationSessionStoreProtocol,
        travel_destination_store: TravelDestinationStoreProtocol,
    ) -> None:
        self._recommendation_session_store = recommendation_session_store
        self._travel_destination_store = travel_destination_store
        logger.info("Session service initialized")

    @staticmethod
    def _extract_recommendation_code(payload: object) -> str | None:
        if not isinstance(payload, dict):
            return None

        code = payload.get("code")
        return code.strip() if isinstance(code, str) and code.strip() else None

    @staticmethod
    def _extract_recommendation_score(payload: object) -> float | None:
        if not isinstance(payload, dict):
            return None

        score = payload.get("score")
        if isinstance(score, int | float):
            return float(score)
        return None

    def _build_recommendation_items(
        self,
        persisted_recommendations: list[object],
    ) -> list[RecommendationItemDto]:
        codes_in_order = [
            code
            for recommendation in persisted_recommendations
            if (code := self._extract_recommendation_code(recommendation)) is not None
        ]
        if not codes_in_order:
            return []

        destinations_by_id: dict[str, TravelDestinationRecord] = {
            destination.id: destination
            for destination in self._travel_destination_store.list_by_ids(codes_in_order)
        }

        recommendation_items: list[RecommendationItemDto] = []
        for recommendation in persisted_recommendations:
            code = self._extract_recommendation_code(recommendation)
            score = self._extract_recommendation_score(recommendation)
            if code is None or score is None:
                continue

            destination = destinations_by_id.get(code)
            recommendation_items.append(
                RecommendationItemDto(
                    id=code,
                    title=destination.region if destination is not None else code,
                    score=score,
                    description=destination.description if destination is not None else "",
                )
            )

        return recommendation_items

    @staticmethod
    def _build_system_messages(
        persisted_messages: list[object],
        fallback_response: str,
    ) -> list[ChatMessageDto]:
        messages: list[ChatMessageDto] = []
        for persisted_message in persisted_messages:
            if not isinstance(persisted_message, dict):
                continue
            messages.append(validate_chat_message(persisted_message))

        if messages:
            return messages

        if fallback_response.strip():
            return [create_text_chat_message(fallback_response)]

        return []

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

        latest_row = rows[-1]
        return SessionStateResponseDto(
            session=session,
            history=[
                SessionHistoryTurnDto(
                    chat_history_number=row.chat_history_number,
                    user_request=row.user_request,
                    system_messages=self._build_system_messages(
                        row.system_messages,
                        row.system_response,
                    ),
                )
                for row in rows
            ],
            last_recommendation_result=self._build_recommendation_items(latest_row.recommendations),
        )

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
