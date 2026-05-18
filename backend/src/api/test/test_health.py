import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.app import create_app
from api.core.configuration import ApiConfiguration
from api.core.configuration import ApiEnvironment
from api.core.configuration import ApiLogLevel
from api.schemas.chat_message import create_text_chat_message
from api.schemas.recommendation import RecommendationRequestDto
from api.schemas.recommendation import RecommendationResponseDto
from api.schemas.session import SessionCreateRequestDto
from api.schemas.session import SessionCreateResponseDto
from api.schemas.session import SessionDeleteResponseDto
from api.schemas.session import SessionRefDto
from api.schemas.session import SessionStateResponseDto
from storage.health import StorageHealthReport


class FakeRecommendationService:
    def chat(self, request: RecommendationRequestDto) -> RecommendationResponseDto:
        _ = request
        return RecommendationResponseDto(messages=[create_text_chat_message("stub")], recommendations=[])


class FakeSessionService:
    def create_session(self, request: SessionCreateRequestDto | None = None) -> SessionCreateResponseDto:
        _ = request
        return SessionCreateResponseDto(session=SessionRefDto(user_id="u", session_id="s"))

    def get_session(self, session: SessionRefDto) -> SessionStateResponseDto:
        return SessionStateResponseDto(session=session)

    def delete_session(self, session: SessionRefDto) -> SessionDeleteResponseDto:
        return SessionDeleteResponseDto(session=session)


class FakeEmbeddingModel:
    def check_health(self) -> bool:
        return True

    def get_dimentions(self) -> int:
        return 8


class FakeStorage:
    def check_health(self) -> StorageHealthReport:
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


def create_test_client() -> TestClient:
    configuration = ApiConfiguration(
        env=ApiEnvironment.development,
        log_level=ApiLogLevel.info,
        host="127.0.0.1",
        port=8000,
    )
    app = create_app(
        configuration=configuration,
        embedding_model=FakeEmbeddingModel(),
        storage=FakeStorage(),
        recommendation_service=FakeRecommendationService(),
        session_service=FakeSessionService(),
    )
    return TestClient(app)


def create_test_app() -> FastAPI:
    configuration = ApiConfiguration(
        env=ApiEnvironment.development,
        log_level=ApiLogLevel.info,
        host="127.0.0.1",
        port=8000,
    )
    return create_app(
        configuration=configuration,
        embedding_model=FakeEmbeddingModel(),
        storage=FakeStorage(),
        recommendation_service=FakeRecommendationService(),
        session_service=FakeSessionService(),
    )


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
