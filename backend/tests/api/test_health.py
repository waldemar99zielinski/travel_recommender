import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.app import create_app
from api.core.configuration import ApiConfiguration
from api.core.configuration import ApiEnvironment
from api.core.configuration import ApiLogLevel
from api.services.in_memory_session_store import InMemorySessionStore
from api.services.placeholder_recommendation_service import PlaceholderRecommendationService


def create_test_client() -> TestClient:
    configuration = ApiConfiguration(
        env=ApiEnvironment.development,
        log_level=ApiLogLevel.info,
        host="127.0.0.1",
        port=8000,
    )
    session_store = InMemorySessionStore(initial_data={})
    service = PlaceholderRecommendationService(session_store=session_store)
    app = create_app(configuration=configuration, recommendation_service=service)
    return TestClient(app)


def create_test_app() -> FastAPI:
    configuration = ApiConfiguration(
        env=ApiEnvironment.development,
        log_level=ApiLogLevel.info,
        host="127.0.0.1",
        port=8000,
    )
    session_store = InMemorySessionStore(initial_data={})
    service = PlaceholderRecommendationService(session_store=session_store)
    return create_app(configuration=configuration, recommendation_service=service)


class TestHealthEndpoints(unittest.TestCase):
    def test_health_endpoint_returns_ok(self) -> None:
        with create_test_client() as client:
            response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["env"], "development")
        self.assertEqual(body["log_level"], "info")

    def test_health_endpoint_returns_503_when_not_ready(self) -> None:
        app = create_test_app()
        app.state.is_ready = False
        with TestClient(app) as client:
            response = client.get("/health")

        self.assertEqual(response.status_code, 503)
        body = response.json()
        self.assertEqual(body["code"], "service_not_ready")


if __name__ == "__main__":
    unittest.main()
