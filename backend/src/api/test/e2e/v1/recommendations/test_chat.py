from __future__ import annotations

import unittest

import requests
from api.test.e2e.utils.test_configuration import api_base_url


class TestRecommendationsChatE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            response = requests.get(f"{api_base_url()}/health", timeout=5)
            if response.status_code not in {200, 503}:
                raise unittest.SkipTest(
                    "Running backend health endpoint returned unexpected status "
                    f"{response.status_code} at {api_base_url()}/health"
                )
        except requests.RequestException as error:
            raise unittest.SkipTest(
                f"Running backend is not reachable at {api_base_url()}: {error}"
            ) from error

    def test_chat_endpoint_returns_recommendations(self) -> None:
        payload = {
            "user_id": "user-123",
            "session_id": "session-abc",
            "message": "I want a peaceful city break",
        }

        response = requests.post(
            f"{api_base_url()}/api/v1/recommendations/chat",
            json=payload,
            timeout=10,
        )
        body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("messages", body)
        self.assertIn("recommendations", body)
        self.assertIsInstance(body["messages"], list)
        recommendations = body["recommendations"]
        self.assertIsInstance(recommendations, list)

    def test_chat_endpoint_rejects_invalid_payload(self) -> None:
        payload = {
            "user_id": "",
            "session_id": "session-abc",
            "message": "",
        }

        response = requests.post(
            f"{api_base_url()}/api/v1/recommendations/chat",
            json=payload,
            timeout=10,
        )
        body = response.json()

        self.assertEqual(response.status_code, 422)
        self.assertEqual(body["code"], "validation_error")
        self.assertEqual(body["message"], "Request validation failed.")

    def test_chat_endpoint_allows_cors_preflight_for_configured_origin(self) -> None:
        response = requests.options(
            f"{api_base_url()}/api/v1/recommendations/chat",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
            timeout=10,
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
