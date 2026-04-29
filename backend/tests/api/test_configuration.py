import os
import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from api.core.configuration import ApiEnvironment
from api.core.configuration import ApiLogLevel
from api.core.configuration import load_api_configuration


class TestApiConfiguration(unittest.TestCase):
    def test_load_api_configuration_from_environment(self) -> None:
        previous = {
            "API_ENV": os.environ.get("API_ENV"),
            "API_LOG_LEVEL": os.environ.get("API_LOG_LEVEL"),
            "API_HOST": os.environ.get("API_HOST"),
            "API_PORT": os.environ.get("API_PORT"),
            "API_CORS_ALLOW_ORIGINS": os.environ.get("API_CORS_ALLOW_ORIGINS"),
        }
        try:
            os.environ["API_ENV"] = "development"
            os.environ["API_LOG_LEVEL"] = "info"
            os.environ["API_HOST"] = "127.0.0.1"
            os.environ["API_PORT"] = "8000"
            os.environ["API_CORS_ALLOW_ORIGINS"] = (
                "http://localhost:5173,http://127.0.0.1:5173"
            )

            configuration = load_api_configuration()

            self.assertEqual(configuration.env, ApiEnvironment.development)
            self.assertEqual(configuration.log_level, ApiLogLevel.info)
            self.assertEqual(configuration.host, "127.0.0.1")
            self.assertEqual(configuration.port, 8000)
            self.assertEqual(
                configuration.cors_allow_origins,
                ["http://localhost:5173", "http://127.0.0.1:5173"],
            )
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


if __name__ == "__main__":
    unittest.main()
