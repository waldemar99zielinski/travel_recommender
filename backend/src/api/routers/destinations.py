from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends

from api.dependencies import get_storage
from api.schemas.destination import DestinationItemDto
from api.schemas.destination import DestinationListResponseDto
from storage.storage import Storage
from utils.logger import LoggerManager

router = APIRouter(prefix="/api/v1/destinations")
logger = LoggerManager.get_logger(__name__)


@router.get("", response_model=DestinationListResponseDto)
def list_destinations(
    storage: Storage = Depends(get_storage),
) -> DestinationListResponseDto:
    logger.info("List all destinations request")
    records = storage.travel_destinations.all()
    destinations = [DestinationItemDto.from_record(r) for r in records]
    logger.info("List all destinations response: total=%d", len(destinations))
    return DestinationListResponseDto(
        destinations=destinations,
        total=len(destinations),
    )
