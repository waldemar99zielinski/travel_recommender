from __future__ import annotations

from typing import Any

from api.core.configuration import ApiConfiguration
from api.core.configuration import ApiEnvironment

DEFAULT_DEVELOPMENT_CORS_ALLOW_ORIGIN_REGEX = (
    r"^https?://(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$"
)


def build_cors_middleware_options(configuration: ApiConfiguration) -> dict[str, Any]:
    allow_origins = [origin.rstrip("/") for origin in configuration.cors_allow_origins]
    allow_origin_regex = configuration.cors_allow_origin_regex

    if (
        not allow_origins
        and allow_origin_regex is None
        and configuration.env == ApiEnvironment.development
    ):
        allow_origin_regex = DEFAULT_DEVELOPMENT_CORS_ALLOW_ORIGIN_REGEX

    options: dict[str, Any] = {
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
        "allow_origins": allow_origins,
    }

    if allow_origin_regex:
        options["allow_origin_regex"] = allow_origin_regex

    return options
