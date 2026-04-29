from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import Response
from fastapi import status

from api.contracts.health_dependencies import EmbeddingHealthDependencyProtocol
from api.contracts.health_dependencies import StorageHealthDependencyProtocol
from api.core.configuration import ApiConfiguration
from api.dependencies import get_api_configuration
from api.dependencies import get_embedding_model
from api.dependencies import get_storage
from api.schemas.common import ErrorResponseDto
from api.schemas.health import ApiHealthCheckDto
from api.schemas.health import EmbeddingsHealthCheckDto
from api.schemas.health import HealthChecksDto
from api.schemas.health import HealthResponseDto
from api.schemas.health import StorageHealthCheckDto
from utils.logger import LoggerManager

router = APIRouter(prefix="/health")
logger = LoggerManager.get_logger(__name__)


@router.get(
    "",
    response_model=HealthResponseDto,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": HealthResponseDto,
            "description": "One or more dependencies are unhealthy.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorResponseDto,
            "description": "Unexpected server error.",
        },
    },
)
def health(
    request: Request,
    response: Response,
    configuration: ApiConfiguration = Depends(get_api_configuration),
    embedding_model: EmbeddingHealthDependencyProtocol = Depends(get_embedding_model),
    storage: StorageHealthDependencyProtocol = Depends(get_storage),
) -> HealthResponseDto:
    logger.info("Health check requested")
    api_healthy = bool(getattr(request.app.state, "is_ready", False))

    try:
        embeddings_healthy = bool(embedding_model.check_health())
        embeddings_details = (
            "Embedding provider is healthy."
            if embeddings_healthy
            else "Embedding provider health check returned false."
        )
    except Exception as error:
        embeddings_healthy = False
        embeddings_details = f"Embedding health check failed: {error}"

    embeddings_dimensions: int | None = None
    if embeddings_healthy:
        try:
            embeddings_dimensions = embedding_model.get_dimentions()
        except Exception as error:
            embeddings_healthy = False
            embeddings_details = f"Embedding dimensions probe failed: {error}"

    try:
        storage_report = storage.check_health()
    except Exception as error:
        storage_report = None
        storage_details = f"Storage health check failed: {error}"
    else:
        storage_details = storage_report.details

    storage_healthy = bool(storage_report is not None and storage_report.is_healthy)
    is_healthy = bool(api_healthy and embeddings_healthy and storage_healthy)

    if not is_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        logger.warning(
            "Health check failed: api_healthy=%s embeddings_healthy=%s storage_healthy=%s",
            api_healthy,
            embeddings_healthy,
            storage_healthy,
        )
    else:
        logger.info("Health check passed")

    return HealthResponseDto(
        status="ok" if is_healthy else "degraded",
        env=configuration.env.value,
        log_level=configuration.log_level.value,
        checks=HealthChecksDto(
            api=ApiHealthCheckDto(
                healthy=api_healthy,
                status="ok" if api_healthy else "error",
                details=(
                    "API lifecycle is ready."
                    if api_healthy
                    else "API lifecycle is not ready yet."
                ),
            ),
            embeddings=EmbeddingsHealthCheckDto(
                healthy=embeddings_healthy,
                status="ok" if embeddings_healthy else "error",
                details=embeddings_details,
                dimensions=embeddings_dimensions,
            ),
            storage=StorageHealthCheckDto(
                healthy=storage_healthy,
                status="ok" if storage_healthy else "error",
                details=storage_details,
                database_reachable=bool(storage_report and storage_report.database_reachable),
                postgresql_18_compatible=bool(storage_report and storage_report.postgresql_18_compatible),
                pgvector_enabled=bool(storage_report and storage_report.pgvector_enabled),
                pgvector_version_compatible=bool(storage_report and storage_report.pgvector_version_compatible),
                embedding_dimension_matches=bool(storage_report and storage_report.embedding_dimension_matches),
                vector_index_present=bool(storage_report and storage_report.vector_index_present),
            ),
        ),
    )
