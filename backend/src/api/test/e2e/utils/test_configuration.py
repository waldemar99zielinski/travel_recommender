from __future__ import annotations

import os

DEFAULT_API_BASE_URL = "http://127.0.0.1:8000"
API_E2E_BASE_URL_ENV = "API_E2E_BASE_URL"


def api_base_url() -> str:
    configured_base_url = os.getenv(API_E2E_BASE_URL_ENV, DEFAULT_API_BASE_URL)
    return configured_base_url.rstrip("/")
