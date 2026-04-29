from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from api.app import create_app
from api.core.configuration import ApiConfiguration
from api.core.configuration import ApiEnvironment
from api.core.configuration import ApiLogLevel
from api.schemas.recommendation import RecommendationRequestDto
from api.schemas.recommendation import RecommendationResponseDto
from storage.health import StorageHealthReport


class _FakeRecommendationService:
    def chat(self, request: RecommendationRequestDto) -> RecommendationResponseDto:
        raise NotImplementedError


class _FakeSessionService:
    def create_session(self, request=None):
        raise NotImplementedError

    def get_session(self, session):
        raise NotImplementedError

    def delete_session(self, session):
        raise NotImplementedError


class _FakeEmbeddingModel:
    def __init__(self, *, healthy: bool = True, dimensions: int = 8, raise_error: bool = False) -> None:
        self._healthy = healthy
        self._dimensions = dimensions
        self._raise_error = raise_error

    def check_health(self) -> bool:
        if self._raise_error:
            raise RuntimeError("embedding backend unavailable")
        return self._healthy

    def get_dimentions(self) -> int:
        return self._dimensions


class _FakeStorage:
    def __init__(self, *, report: StorageHealthReport, raise_error: bool = False) -> None:
        self._report = report
        self._raise_error = raise_error

    def check_health(self) -> StorageHealthReport:
        if self._raise_error:
            raise RuntimeError("database offline")
        return self._report


def _healthy_storage_report() -> StorageHealthReport:
    return StorageHealthReport(
        is_healthy=True,
        database_reachable=True,
        postgresql_18_compatible=True,
        pgvector_enabled=True,
        pgvector_version_compatible=True,
        embedding_dimension_matches=True,
        vector_index_present=True,
        details="ok",
    )


def _unhealthy_storage_report() -> StorageHealthReport:
    return StorageHealthReport(
        is_healthy=False,
        database_reachable=True,
        postgresql_18_compatible=True,
        pgvector_enabled=True,
        pgvector_version_compatible=True,
        embedding_dimension_matches=False,
        vector_index_present=True,
        details="Storage health check failed: embedding_dimension_matches=false",
    )


class TestHealthRouter(unittest.TestCase):
    def setUp(self) -> None:
        self.configuration = ApiConfiguration(
            env=ApiEnvironment.development,
            log_level=ApiLogLevel.info,
            host="localhost",
            port=8000,
            cors_allow_origins=[],
        )

    def test_health_returns_ok_with_component_reports(self) -> None:
        app = create_app(
            configuration=self.configuration,
            embedding_model=_FakeEmbeddingModel(healthy=True, dimensions=8),
            storage=_FakeStorage(report=_healthy_storage_report()),
            recommendation_service=_FakeRecommendationService(),
            session_service=_FakeSessionService(),
        )

        with TestClient(app) as client:
            response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["env"], "development")
        self.assertEqual(body["log_level"], "info")
        self.assertTrue(body["checks"]["api"]["healthy"])
        self.assertTrue(body["checks"]["embeddings"]["healthy"])
        self.assertEqual(body["checks"]["embeddings"]["dimensions"], 8)
        self.assertTrue(body["checks"]["storage"]["healthy"])

    def test_health_returns_degraded_when_embedding_is_unhealthy(self) -> None:
        app = create_app(
            configuration=self.configuration,
            embedding_model=_FakeEmbeddingModel(healthy=False),
            storage=_FakeStorage(report=_healthy_storage_report()),
            recommendation_service=_FakeRecommendationService(),
            session_service=_FakeSessionService(),
        )

        with TestClient(app) as client:
            response = client.get("/health")

        self.assertEqual(response.status_code, 503)
        body = response.json()
        self.assertEqual(body["status"], "degraded")
        self.assertEqual(body["checks"]["embeddings"]["status"], "error")
        self.assertIsNone(body["checks"]["embeddings"]["dimensions"])

    def test_health_returns_degraded_when_storage_is_unhealthy(self) -> None:
        app = create_app(
            configuration=self.configuration,
            embedding_model=_FakeEmbeddingModel(healthy=True),
            storage=_FakeStorage(report=_unhealthy_storage_report()),
            recommendation_service=_FakeRecommendationService(),
            session_service=_FakeSessionService(),
        )

        with TestClient(app) as client:
            response = client.get("/health")

        self.assertEqual(response.status_code, 503)
        body = response.json()
        self.assertEqual(body["status"], "degraded")
        self.assertEqual(body["checks"]["storage"]["status"], "error")
        self.assertFalse(body["checks"]["storage"]["embedding_dimension_matches"])

    def test_health_returns_degraded_when_api_is_not_ready(self) -> None:
        app = create_app(
            configuration=self.configuration,
            embedding_model=_FakeEmbeddingModel(healthy=True),
            storage=_FakeStorage(report=_healthy_storage_report()),
            recommendation_service=_FakeRecommendationService(),
            session_service=_FakeSessionService(),
        )

        with TestClient(app) as client:
            app.state.is_ready = False
            response = client.get("/health")

        self.assertEqual(response.status_code, 503)
        body = response.json()
        self.assertEqual(body["status"], "degraded")
        self.assertEqual(body["checks"]["api"]["status"], "error")


if __name__ == "__main__":
    unittest.main()
