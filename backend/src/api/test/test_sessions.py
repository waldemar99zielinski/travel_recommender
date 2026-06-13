import unittest
from uuid import uuid4

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
from api.services.session_service import SessionService
from storage.health import StorageHealthReport
from storage.models.chat_record import ChatRecord


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


class FakeChatStore:
    def __init__(self, rows: list[ChatRecord] | None = None) -> None:
        self._rows = list(rows or [])

    def load_session(self, user_id: str, session_id: str) -> list[ChatRecord]:
        return [
            row
            for row in self._rows
            if str(row.user_id) == user_id and str(row.session_id) == session_id
        ]

    def delete_session(self, user_id: str, session_id: str) -> None:
        self._rows = [
            row
            for row in self._rows
            if not (str(row.user_id) == user_id and str(row.session_id) == session_id)
        ]


class FakeTravelDestinationStore:
    pass


def create_test_client(session_service: object | None = None) -> TestClient:
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
        session_service=session_service or FakeSessionService(),
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

    def test_get_session_returns_cors_header(self) -> None:
        with create_test_client() as client:
            response = client.get(
                "/api/v1/sessions/user-1/session-1",
                headers={"Origin": "http://localhost:5173"},
            )

        self.assertEqual(response.headers.get("access-control-allow-origin"), "http://localhost:5173")

    def test_get_session_returns_persisted_history_without_region_id_arrays(self) -> None:
        user_id = uuid4()
        session_id = uuid4()
        persisted_row = ChatRecord(
            user_id=user_id,
            session_id=session_id,
            chat_history_number=0,
            user_request="Recommend a quiet beach trip",
            system_response="Consider the Algarve.",
            synthesized_query="quiet beach trip europe",
            recommendations=[{"region_id": "PRT_ALG", "region_name": "Algarve"}],
            travel_destination_filter={"seasonality": {"season": "summer"}},
            travel_destinations_evaluations=[],
            graph_version="v2",
        )
        session_service = SessionService(
            chat_store=FakeChatStore([persisted_row]),
            travel_destination_store=FakeTravelDestinationStore(),
        )

        with create_test_client(session_service=session_service) as client:
            response = client.get(f"/api/v1/sessions/{user_id}/{session_id}")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["session"]["version"], "v2")
        self.assertEqual(len(body["chat_history"]), 1)
        self.assertEqual(body["chat_history"][0]["included_regions_ids"], [])
        self.assertEqual(body["chat_history"][0]["excluded_regions_ids"], [])
        self.assertEqual(
            body["chat_history"][0]["travel_destination_filter"],
            {"seasonality": {"season": "summer"}},
        )


if __name__ == "__main__":
    unittest.main()
