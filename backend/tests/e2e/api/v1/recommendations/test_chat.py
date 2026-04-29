from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[5] / "src"))

from fastapi.testclient import TestClient

from api.app import create_app
from api.core.configuration import ApiConfiguration
from api.core.configuration import ApiEnvironment
from api.core.configuration import ApiLogLevel
from api.schemas.recommendation import RecommendationItemDto
from api.schemas.recommendation import RecommendationRequestDto
from api.schemas.recommendation import RecommendationResponseDto


class FakeRecommendationService:
    def chat(self, request: RecommendationRequestDto) -> RecommendationResponseDto:
        return RecommendationResponseDto(
            message=f"Recommendations for: {request.message}",
            recommendations=[
                RecommendationItemDto(
                    id="destination-1",
                    title="Zurich",
                    score=0.91,
                    description="A quiet city with lake views and nearby mountains.",
                ),
            ],
        )


def create_test_client() -> TestClient:
    configuration = ApiConfiguration(
        env=ApiEnvironment.development,
        log_level=ApiLogLevel.info,
        host="127.0.0.1",
        port=8000,
        cors_allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    )
    app = create_app(
        configuration=configuration,
        recommendation_service=FakeRecommendationService(),
    )
    return TestClient(app)


class TestRecommendationsChatE2E(unittest.TestCase):
    def test_chat_endpoint_returns_recommendations(self) -> None:
        payload = {
            "user_id": "user-123",
            "session_id": "session-abc",
            "message": "I want a peaceful city break",
        }

        with create_test_client() as client:
            response = client.post("/api/v1/recommendations/chat", json=payload)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(
            body["message"],
            "Recommendations for: I want a peaceful city break",
        )
        self.assertEqual(len(body["recommendations"]), 1)
        self.assertEqual(body["recommendations"][0]["id"], "destination-1")
        self.assertEqual(body["recommendations"][0]["title"], "Zurich")

    def test_chat_endpoint_rejects_invalid_payload(self) -> None:
        payload = {
            "user_id": "",
            "session_id": "session-abc",
            "message": "",
        }

        with create_test_client() as client:
            response = client.post("/api/v1/recommendations/chat", json=payload)

        self.assertEqual(response.status_code, 422)
        body = response.json()
        self.assertEqual(body["code"], "validation_error")
        self.assertEqual(body["message"], "Request validation failed.")

    def test_chat_endpoint_allows_cors_preflight_for_configured_origin(self) -> None:
        with create_test_client() as client:
            response = client.options(
                "/api/v1/recommendations/chat",
                headers={
                    "Origin": "http://localhost:5173",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "content-type",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("access-control-allow-origin"),
            "http://localhost:5173",
        )
        self.assertEqual(
            response.headers.get("access-control-allow-credentials"),
            "true",
        )


if __name__ == "__main__":
    unittest.main()
