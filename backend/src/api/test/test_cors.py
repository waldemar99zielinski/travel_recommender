import unittest

from api.core.configuration import ApiConfiguration
from api.core.configuration import ApiEnvironment
from api.core.configuration import ApiLogLevel
from api.core.cors import DEFAULT_DEVELOPMENT_CORS_ALLOW_ORIGIN_REGEX
from api.core.cors import build_cors_middleware_options


def build_configuration(
    *,
    env: ApiEnvironment = ApiEnvironment.development,
    cors_allow_origins: list[str] | None = None,
    cors_allow_origin_regex: str | None = None,
) -> ApiConfiguration:
    resolved_cors_allow_origins = [] if cors_allow_origins is None else cors_allow_origins

    return ApiConfiguration(
        env=env,
        log_level=ApiLogLevel.info,
        host="127.0.0.1",
        port=8000,
        cors_allow_origins=resolved_cors_allow_origins,
        cors_allow_origin_regex=cors_allow_origin_regex,
    )


class TestCorsMiddlewareOptions(unittest.TestCase):
    def test_uses_explicit_allow_origins_when_configured(self) -> None:
        configuration = build_configuration(
            cors_allow_origins=["http://localhost:5173/", "http://127.0.0.1:5174"],
        )

        options = build_cors_middleware_options(configuration)

        self.assertEqual(
            options["allow_origins"],
            ["http://localhost:5173", "http://127.0.0.1:5174"],
        )
        self.assertNotIn("allow_origin_regex", options)

    def test_applies_localhost_regex_fallback_in_development(self) -> None:
        configuration = build_configuration(cors_allow_origins=[])

        options = build_cors_middleware_options(configuration)

        self.assertEqual(
            options["allow_origin_regex"],
            DEFAULT_DEVELOPMENT_CORS_ALLOW_ORIGIN_REGEX,
        )

    def test_does_not_apply_localhost_regex_fallback_in_production(self) -> None:
        configuration = build_configuration(
            env=ApiEnvironment.production,
            cors_allow_origins=[],
        )

        options = build_cors_middleware_options(configuration)

        self.assertEqual(options["allow_origins"], [])
        self.assertNotIn("allow_origin_regex", options)


if __name__ == "__main__":
    unittest.main()
