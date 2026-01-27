from enum import Enum
from pydantic_settings import BaseSettings
from pydantic import (
    Field,
)

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
    env: Environment = Field(..., description="The environment the application is running in")
    log_level: LogLevel = Field(..., description="The logging level for the application")
