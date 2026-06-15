from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.contracts.health_dependencies import EmbeddingHealthDependencyProtocol
from api.contracts.health_dependencies import StorageHealthDependencyProtocol
from api.contracts.recommendation_service import RecommendationServiceProtocol
from api.contracts.session_service import SessionServiceProtocol
from api.core.configuration import ApiConfiguration
from api.core.cors import build_cors_middleware_options
from api.core.handlers import register_exception_handlers
from api.lifecycle import create_lifespan
from api.routers import destinations
from api.routers import health
from api.routers import recommendations_v2
from api.routers import sessions
from api.routers import survey


def create_app(
    *,
    configuration: ApiConfiguration,
    embedding_model: EmbeddingHealthDependencyProtocol,
    storage: StorageHealthDependencyProtocol,
    recommendation_service: RecommendationServiceProtocol | None = None,
    recommendation_v2_service: Any | None = None,
    session_service: SessionServiceProtocol,
) -> FastAPI:
    app = FastAPI(lifespan=create_lifespan())

    app.add_middleware(
        CORSMiddleware,
        **build_cors_middleware_options(configuration),
    )

    app.state.api_configuration = configuration
    app.state.embedding_model = embedding_model
    app.state.storage = storage
    app.state.recommendation_service = recommendation_service
    app.state.recommendation_v2_service = recommendation_v2_service
    app.state.session_service = session_service
    app.state.is_ready = False

    app.include_router(destinations.router)
    app.include_router(health.router)
    app.include_router(recommendations_v2.router)

    app.include_router(sessions.router)
    app.include_router(survey.router)

    register_exception_handlers(app)
    return app
