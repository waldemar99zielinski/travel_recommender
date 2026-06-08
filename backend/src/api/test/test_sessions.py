import unittest

from fastapi.testclient import TestClient

from api.app import create_app
from api.core.configuration import ApiConfiguration
from api.core.configuration import ApiEnvironment
from api.core.configuration import ApiLogLevel
from api.core.exceptions import SessionNotFoundError
from api.schemas.chat import create_text_chat_message
from api.schemas.recommendation import RecommendationRequestDto
from api.schemas.recommendation import RecommendationResponseDto
from api.schemas.session import SessionCreateRequestDto
from api.schemas.session import SessionGetRequestDto
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
    def __init__(self) -> None:
        self._sessions: set[tuple[str, str]] = set()

    def create_session(self, request: SessionCreateRequestDto | None = None) -> SessionCreateResponseDto:
        user_id = request.user_id if request is not None and request.user_id is not None else "user-1"
        session = SessionRefDto(user_id=user_id, session_id="session-1")
        self._sessions.add((session.user_id, session.session_id))
        return SessionCreateResponseDto(session=session)

    def get_session(self, session: SessionGetRequestDto) -> SessionStateResponseDto:
        if (session.user_id, session.session_id) not in self._sessions:
            raise SessionNotFoundError(user_id=session.user_id, session_id=session.session_id)
        return SessionStateResponseDto(
            session=SessionRefDto(user_id=session.user_id, session_id=session.session_id),
        )

    def delete_session(self, session: SessionGetRequestDto) -> SessionDeleteResponseDto:
        self._sessions.discard((session.user_id, session.session_id))
        return SessionDeleteResponseDto(
            session=SessionRefDto(user_id=session.user_id, session_id=session.session_id),
        )


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


class TestSessionEndpoints(unittest.TestCase):
    def test_get_session_returns_404_for_missing_session(self) -> None:
        with create_test_client() as client:
            response = client.get("/api/v1/sessions/user-1/session-1")

        self.assertEqual(response.status_code, 404)
        body = response.json()
        self.assertEqual(body["code"], "session_not_found")

    def test_session_lifecycle(self) -> None:
        with create_test_client() as client:
            create_response = client.post("/api/v1/sessions", json={"user_id": "user-1"})
            get_response = client.get("/api/v1/sessions/user-1/session-1")
            delete_response = client.delete("/api/v1/sessions/user-1/session-1")

        self.assertEqual(create_response.status_code, 200)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(delete_response.status_code, 200)
        get_body = get_response.json()
        self.assertEqual(get_body["chat_history"], [])
        self.assertEqual(get_body["session"]["version"], "v1")
        delete_body = delete_response.json()
        self.assertEqual(delete_body["session"]["user_id"], "user-1")
        self.assertEqual(delete_body["session"]["session_id"], "session-1")
        self.assertEqual(delete_body["session"]["version"], "v1")


if __name__ == "__main__":
    unittest.main()
