from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Annotated
from typing import Any

from pydantic import Field
from pydantic import field_validator
from pydantic_settings import BaseSettings
from pydantic_settings import NoDecode
from pydantic_settings import SettingsConfigDict


class ApiEnvironment(str, Enum):
    development = "development"
    staging = "staging"
    production = "production"


class ApiLogLevel(str, Enum):
    debug = "debug"
    verbose = "verbose"
    info = "info"
    warning = "warning"
    error = "error"
    critical = "critical"


class ApiConfiguration(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3] / ".env",
        env_prefix="API_",
        extra="ignore",
    )

    env: ApiEnvironment = ApiEnvironment.development
    log_level: ApiLogLevel = ApiLogLevel.verbose
    host: str = "localhost"
    port: int = 8000
    cors_allow_origins: Annotated[list[str], NoDecode] = Field(default_factory=list)
    cors_allow_origin_regex: str | None = None

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def parse_cors_allow_origins(cls, value: Any) -> list[str] | Any:
        if isinstance(value, str):
            return [
                origin.strip().rstrip("/")
                for origin in value.split(",")
                if origin.strip()
            ]
        return value


def load_api_configuration() -> ApiConfiguration:
    return ApiConfiguration()
