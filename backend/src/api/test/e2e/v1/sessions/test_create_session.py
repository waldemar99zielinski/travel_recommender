from __future__ import annotations

import unittest

import requests
from api.test.e2e.utils.test_configuration import api_base_url


class TestCreateSessionE2E(unittest.TestCase):
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

    def test_create_session_generates_user_id_when_missing(self) -> None:
        response = requests.post(
            f"{api_base_url()}/api/v1/sessions",
            json={},
            timeout=10,
        )
        body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(body.keys()), {"session"})
        self.assertTrue(body["session"]["user_id"])
        self.assertTrue(body["session"]["session_id"])

    def test_create_session_uses_given_user_id(self) -> None:
        response = requests.post(
            f"{api_base_url()}/api/v1/sessions",
            json={"user_id": "user-123"},
            timeout=10,
        )
        body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(body.keys()), {"session"})
        self.assertEqual(body["session"]["user_id"], "user-123")


if __name__ == "__main__":
    unittest.main()
