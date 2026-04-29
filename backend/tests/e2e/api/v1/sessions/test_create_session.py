from __future__ import annotations

import sys
import unittest
from pathlib import Path
from uuid import uuid4

sys.path.append(str(Path(__file__).resolve().parents[5] / "src"))

from fastapi.testclient import TestClient

from api.app import create_app
from api.core.configuration import ApiConfiguration
from api.core.configuration import ApiEnvironment
from api.core.configuration import ApiLogLevel
from api.core.exceptions import SessionNotFoundError
from api.schemas.recommendation import RecommendationRequestDto
from api.schemas.recommendation import RecommendationResponseDto
from api.schemas.session import SessionCreateRequestDto
from api.schemas.session import SessionCreateResponseDto
from api.schemas.session import SessionDeleteResponseDto
from api.schemas.session import SessionRefDto
from api.schemas.session import SessionStateResponseDto
from storage.health import StorageHealthReport


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


class FakeRecommendationService:
    def __init__(self) -> None:
        self._sessions: dict[tuple[str, str], list[str]] = {}

    def create_session(
        self,
        request: SessionCreateRequestDto | None = None,
    ) -> SessionCreateResponseDto:
        user_id = request.user_id.strip() if request is not None and request.user_id is not None else ""
        if user_id == "":
            user_id = str(uuid4())

        session = SessionRefDto(user_id=user_id, session_id=str(uuid4()))
        self._sessions[(session.user_id, session.session_id)] = []
        return SessionCreateResponseDto(session=session)

    def get_session(self, session: SessionRefDto) -> SessionStateResponseDto:
        key = (session.user_id, session.session_id)
        if self._sessions.get(key) is None:
            raise SessionNotFoundError(user_id=session.user_id, session_id=session.session_id)

        return SessionStateResponseDto(session=session)

    def delete_session(self, session: SessionRefDto) -> SessionDeleteResponseDto:
        key = (session.user_id, session.session_id)
        self._sessions.pop(key, None)
        return SessionDeleteResponseDto(session=session)

    def chat(self, request: RecommendationRequestDto) -> RecommendationResponseDto:
        _ = request
        return RecommendationResponseDto(message="stub", recommendations=[])


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
    )
    return TestClient(app)


class TestCreateSessionE2E(unittest.TestCase):
    def test_create_session_generates_user_id_when_missing(self) -> None:
        with create_test_client() as client:
            response = client.post("/api/v1/sessions", json={})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(set(body.keys()), {"session"})
        self.assertTrue(body["session"]["user_id"])
        self.assertTrue(body["session"]["session_id"])

    def test_create_session_uses_given_user_id(self) -> None:
        with create_test_client() as client:
            response = client.post("/api/v1/sessions", json={"user_id": "user-123"})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(set(body.keys()), {"session"})
        self.assertEqual(body["session"]["user_id"], "user-123")


if __name__ == "__main__":
    unittest.main()
