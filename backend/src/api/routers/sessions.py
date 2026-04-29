from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends

from api.contracts.session_service import SessionServiceProtocol
from api.dependencies import get_session_service
from api.schemas.session import SessionCreateRequestDto
from api.schemas.session import SessionCreateResponseDto
from api.schemas.session import SessionDeleteResponseDto
from api.schemas.session import SessionRefDto
from api.schemas.session import SessionStateResponseDto
from utils.logger import LoggerManager

router = APIRouter(prefix="/api/v1/sessions")
logger = LoggerManager.get_logger(__name__)


@router.post("", response_model=SessionCreateResponseDto)
def create_session(
    payload: SessionCreateRequestDto | None = None,
    service: SessionServiceProtocol = Depends(get_session_service),
) -> SessionCreateResponseDto:
    logger.info("Create session request: user_id=%s", payload.user_id if payload is not None else None)
    return service.create_session(payload)


@router.get("/{user_id}/{session_id}", response_model=SessionStateResponseDto)
def get_session(
    user_id: str,
    session_id: str,
    service: SessionServiceProtocol = Depends(get_session_service),
) -> SessionStateResponseDto:
    logger.info("Get session request: user_id=%s, session_id=%s", user_id, session_id)
    return service.get_session(SessionRefDto(user_id=user_id, session_id=session_id))


@router.delete("/{user_id}/{session_id}", response_model=SessionDeleteResponseDto)
def delete_session(
    user_id: str,
    session_id: str,
    service: SessionServiceProtocol = Depends(get_session_service),
) -> SessionDeleteResponseDto:
    logger.info("Delete session request: user_id=%s, session_id=%s", user_id, session_id)
    return service.delete_session(SessionRefDto(user_id=user_id, session_id=session_id))
