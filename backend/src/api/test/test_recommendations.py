from __future__ import annotations

import json
import unittest
from collections.abc import AsyncGenerator

from fastapi.testclient import TestClient

from api.app import create_app
from api.core.configuration import ApiConfiguration
from api.core.configuration import ApiEnvironment
from api.core.configuration import ApiLogLevel
from api.schemas.recommendation import RecommendationRequestDto
from api.schemas.session import SessionCreateRequestDto
from api.schemas.session import SessionGetRequestDto
from api.schemas.session import SessionCreateResponseDto
from api.schemas.session import SessionDeleteResponseDto
from api.schemas.session import SessionRefDto
from api.schemas.session import SessionStateResponseDto
from api.utils.sse import MESSAGE_DELIMITER, format_sse
from storage.health import StorageHealthReport


class FakeRecommendationService:
    async def chat_stream(
        self,
        request: RecommendationRequestDto,
    ) -> AsyncGenerator[str, None]:
        yield format_sse("init", {})
        yield format_sse(
            "recommendation",
            {
                "user_id": request.session.user_id,
                "session_id": request.session.session_id,
                "chat_history_number": 0,
                "user_request": request.message,
                "system_response": f"Recommendations for: {request.message}",
                "recommendations": [{"region_id": "ch-zurich", "explanation": "Good match for the requested trip."}],
                "travel_destinations_evaluations": [],
                "included_regions_ids": [],
                "excluded_regions_ids": [],
            },
        )
        yield format_sse("completed", {})


class FakeSessionService:
    def create_session(self, request: SessionCreateRequestDto | None = None) -> SessionCreateResponseDto:
        _ = request
        return SessionCreateResponseDto(session=SessionRefDto(user_id="u", session_id="s"))

    def get_session(self, session: SessionGetRequestDto) -> SessionStateResponseDto:
        return SessionStateResponseDto(
            session=SessionRefDto(user_id=session.user_id, session_id=session.session_id),
        )

    def delete_session(self, session: SessionGetRequestDto) -> SessionDeleteResponseDto:
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
    return create_test_client_for_env(ApiEnvironment.development)


def create_test_client_for_env(env: ApiEnvironment) -> TestClient:
    configuration = ApiConfiguration(
        env=env,
        log_level=ApiLogLevel.info,
        host="127.0.0.1",
        port=8000,
    )
    fake = FakeRecommendationService()
    app = create_app(
        configuration=configuration,
        embedding_model=FakeEmbeddingModel(),
        storage=FakeStorage(),
        recommendation_v0_service=fake,
        recommendation_v1_service=fake,
        session_service=FakeSessionService(),
    )
    return TestClient(app)


def _parse_sse_events(text: str) -> list[dict]:
    events = []
    for block in text.strip().split(MESSAGE_DELIMITER):
        if not block.strip():
            continue
        lines = block.strip().split("\n")
        event = ""
        data = ""
        for line in lines:
            if line.startswith("event: "):
                event = line[7:]
            elif line.startswith("data: "):
                data = line[6:]
        if event or data:
            events.append({"event": event, "data": json.loads(data) if data else {}})
    return events


class TestRecommendationEndpoints(unittest.TestCase):
    def test_chat_v0_endpoint_returns_sse_stream(self) -> None:
        payload = {
            "session": {"user_id": "user-1", "session_id": "session-1"},
            "message": "Recommend a calm trip",
        }

        with create_test_client() as client:
            response = client.post("/api/v0/recommendations/chat", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "text/event-stream; charset=utf-8")

        events = _parse_sse_events(response.text)
        self.assertGreaterEqual(len(events), 2)
        self.assertEqual(events[0]["event"], "init")
        recommendation_event = next(e for e in events if e["event"] == "recommendation")
        self.assertEqual(recommendation_event["data"]["user_request"], "Recommend a calm trip")

    def test_chat_endpoint_returns_sse_stream(self) -> None:
        payload = {
            "session": {"user_id": "user-1", "session_id": "session-1"},
            "message": "Recommend a calm trip",
        }

        with create_test_client() as client:
            response = client.post("/api/v1/recommendations/chat", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "text/event-stream; charset=utf-8")

        events = _parse_sse_events(response.text)
        self.assertGreaterEqual(len(events), 2)

        self.assertEqual(events[0]["event"], "init")
        self.assertEqual(events[0]["data"], {})

        recommendation_event = next(e for e in events if e["event"] == "recommendation")
        self.assertIn("system_response", recommendation_event["data"])
        self.assertIn("recommendations", recommendation_event["data"])
        self.assertEqual(recommendation_event["data"]["user_request"], "Recommend a calm trip")
        self.assertEqual(
            recommendation_event["data"]["system_response"],
            "Recommendations for: Recommend a calm trip",
        )
        self.assertEqual(len(recommendation_event["data"]["recommendations"]), 1)

        completed_event = next(e for e in events if e["event"] == "completed")
        self.assertEqual(completed_event["data"], {})

    def test_chat_endpoint_validates_payload(self) -> None:
        payload = {
            "session": {"user_id": "", "session_id": "session-1"},
            "message": "",
        }

        with create_test_client() as client:
            response = client.post("/api/v1/recommendations/chat", json=payload)

        self.assertEqual(response.status_code, 422)
        body = response.json()
        self.assertEqual(body["code"], "validation_error")

    def test_chat_v0_endpoint_returns_not_implemented_in_production(self) -> None:
        payload = {
            "session": {"user_id": "user-1", "session_id": "session-1"},
            "message": "Recommend a calm trip",
        }

        with create_test_client_for_env(ApiEnvironment.production) as client:
            response = client.post("/api/v0/recommendations/chat", json=payload)

        self.assertEqual(response.status_code, 501)
        body = response.json()
        self.assertEqual(body["code"], "not_implemented")
        self.assertEqual(body["details"], {"environment": "production", "version": "v0"})

    def test_chat_v1_endpoint_returns_not_implemented_in_production(self) -> None:
        payload = {
            "session": {"user_id": "user-1", "session_id": "session-1"},
            "message": "Recommend a calm trip",
        }

        with create_test_client_for_env(ApiEnvironment.production) as client:
            response = client.post("/api/v1/recommendations/chat", json=payload)

        self.assertEqual(response.status_code, 501)
        body = response.json()
        self.assertEqual(body["code"], "not_implemented")
        self.assertEqual(body["details"], {"environment": "production", "version": "v1"})

if __name__ == "__main__":
    unittest.main()
