from __future__ import annotations

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
from api.routers import health
from api.routers import recommendations
from api.routers import sessions


def create_app(
    *,
    configuration: ApiConfiguration,
    embedding_model: EmbeddingHealthDependencyProtocol,
    storage: StorageHealthDependencyProtocol,
    recommendation_service: RecommendationServiceProtocol,
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
    app.state.session_service = session_service
    app.state.is_ready = False

    app.include_router(health.router)
    app.include_router(recommendations.router)
    app.include_router(sessions.router)

    register_exception_handlers(app)
    return app
