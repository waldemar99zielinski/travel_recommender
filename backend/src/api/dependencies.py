from __future__ import annotations

from fastapi import Request

from api.contracts.health_dependencies import EmbeddingHealthDependencyProtocol
from api.contracts.health_dependencies import StorageHealthDependencyProtocol
from api.contracts.recommendation_service import RecommendationServiceProtocol
from api.contracts.session_service import SessionServiceProtocol
from api.core.configuration import ApiConfiguration
from api.core.exceptions import DependencyNotConfiguredError


def get_api_configuration(request: Request) -> ApiConfiguration:
    configuration = getattr(request.app.state, "api_configuration", None)
    if configuration is None:
        raise DependencyNotConfiguredError(dependency_name="api_configuration")
    return configuration


def get_recommendation_service(request: Request) -> RecommendationServiceProtocol:
    service = getattr(request.app.state, "recommendation_service", None)
    if service is None:
        raise DependencyNotConfiguredError(dependency_name="recommendation_service")
    return service


def get_recommendation_v2_service(request: Request) -> RecommendationServiceProtocol:
    service = getattr(request.app.state, "recommendation_v2_service", None)
    if service is None:
        raise DependencyNotConfiguredError(dependency_name="recommendation_v2_service")
    return service


def get_recommendation_v3_service(request: Request) -> RecommendationServiceProtocol:
    service = getattr(request.app.state, "recommendation_v3_service", None)
    if service is None:
        raise DependencyNotConfiguredError(dependency_name="recommendation_v3_service")
    return service


def get_session_service(request: Request) -> SessionServiceProtocol:
    service = getattr(request.app.state, "session_service", None)
    if service is None:
        raise DependencyNotConfiguredError(dependency_name="session_service")
    return service


def get_embedding_model(request: Request) -> EmbeddingHealthDependencyProtocol:
    embedding_model = getattr(request.app.state, "embedding_model", None)
    if embedding_model is None:
        raise DependencyNotConfiguredError(dependency_name="embedding_model")
    return embedding_model


def get_storage(request: Request) -> StorageHealthDependencyProtocol:
    storage = getattr(request.app.state, "storage", None)
    if storage is None:
        raise DependencyNotConfiguredError(dependency_name="storage")
    return storage
