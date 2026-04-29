from __future__ import annotations

from enum import Enum

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
    '''
    Configuration settings for the recommender application.
    '''
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    env: Environment = Field(Environment.development, description="The environment the application is running in")
    log_level: LogLevel = Field(LogLevel.info, description="The logging level for the application")
