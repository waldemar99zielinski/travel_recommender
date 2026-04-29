import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

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
        self.assertEqual(body["status"], "placeholder")
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


if __name__ == "__main__":
    unittest.main()
