from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import (
    Field,
)
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Environment(str, Enum):
    development = "development"
    staging = "staging"
    production = "production"


class LogLevel(str, Enum):
    debug = "debug"
    verbose = "verbose"
    info = "info"
    warning = "warning"
    error = "error"


class Configuration(BaseSettings):
    """Configuration settings for the recommender application."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3] / ".env",
        extra="ignore",
    )

    env: Environment = Field(
        Environment.development,
        description="The environment the application is running in",
    )
    log_level: LogLevel = Field(
        LogLevel.info,
        description="The logging level for the application",
    )
    tavily_api_key: str = Field(
        "",
        description="API key for the Tavily web search service",
    )
    recommendation_limit: int = Field(
        5,
        description="The maximum number of recommendations to return to the user",
    )
