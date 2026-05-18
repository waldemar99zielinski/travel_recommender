import unittest

from fastapi.testclient import TestClient

from api.app import create_app
from api.core.configuration import ApiConfiguration
from api.core.configuration import ApiEnvironment
from api.core.configuration import ApiLogLevel
from api.schemas.chat_message import create_text_chat_message
from api.schemas.recommendation import RecommendationItemDto
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
        return RecommendationResponseDto(
            messages=[create_text_chat_message(f"Recommendations for: {request.message}")],
            recommendations=[
                RecommendationItemDto(
                    id="destination-1",
                    title="Zurich",
                    score=0.91,
                    description="A quiet city with lake views and nearby mountains.",
                ),
            ],
        )


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


class TestRecommendationEndpoints(unittest.TestCase):
    def test_chat_endpoint_returns_placeholder_response(self) -> None:
        payload = {
            "user_id": "user-1",
            "session_id": "session-1",
            "message": "Recommend a calm trip",
        }

        with create_test_client() as client:
            response = client.post("/api/v1/recommendations/chat", json=payload)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body["messages"]), 1)
        self.assertEqual(body["messages"][0]["type"], "text")
        self.assertEqual(
            body["messages"][0]["context"]["text"],
            "Recommendations for: Recommend a calm trip",
        )
        self.assertEqual(len(body["recommendations"]), 1)

    def test_chat_endpoint_validates_payload(self) -> None:
        payload = {
            "user_id": "",
            "session_id": "session-1",
            "message": "",
        }

        with create_test_client() as client:
            response = client.post("/api/v1/recommendations/chat", json=payload)

        self.assertEqual(response.status_code, 422)
        body = response.json()
        self.assertEqual(body["code"], "validation_error")

    def test_chat_v2_endpoint_returns_placeholder_response(self) -> None:
        payload = {
            "user_id": "user-1",
            "session_id": "session-1",
            "message": "Recommend a calm trip",
        }

        with create_test_client() as client:
            response = client.post("/api/v2/recommendations/chat", json=payload)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body["messages"]), 1)
        self.assertEqual(body["messages"][0]["type"], "text")
        self.assertEqual(
            body["messages"][0]["context"]["text"],
            "Recommendations for: Recommend a calm trip",
        )
        self.assertEqual(len(body["recommendations"]), 1)


if __name__ == "__main__":
    unittest.main()
