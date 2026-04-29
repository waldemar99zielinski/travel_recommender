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


class TestSessionEndpoints(unittest.TestCase):
    def test_get_session_returns_404_for_missing_session(self) -> None:
        with create_test_client() as client:
            response = client.get("/api/v1/sessions/user-1/session-1")

        self.assertEqual(response.status_code, 404)
        body = response.json()
        self.assertEqual(body["code"], "session_not_found")

    def test_session_lifecycle(self) -> None:
        payload = {
            "user_id": "user-1",
            "session_id": "session-1",
            "message": "Suggest mountains",
        }

        with create_test_client() as client:
            chat_response = client.post("/api/v1/recommendations/chat", json=payload)
            get_response = client.get("/api/v1/sessions/user-1/session-1")
            delete_response = client.delete("/api/v1/sessions/user-1/session-1")

        self.assertEqual(chat_response.status_code, 200)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(delete_response.status_code, 200)
        delete_body = delete_response.json()
        self.assertEqual(delete_body["session"]["user_id"], "user-1")
        self.assertEqual(delete_body["session"]["session_id"], "session-1")


if __name__ == "__main__":
    unittest.main()
