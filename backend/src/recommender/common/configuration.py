from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import BaseModel
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


class SqlStoreConfiguration(BaseModel):
    """Configuration for SQL-backed travel destination store."""

    db_url: str = Field(
        default="sqlite:///store_data/travel_destinations.sqlite3",
        description="SQLAlchemy database URL for the travel destination SQL store",
    )


class VectorStoreConfiguration(BaseModel):
    """Configuration for vector-backed travel destination store."""

    db_path: str = Field(
        default="store_data/travel_destinations_vector_index",
        description="Filesystem path for the persisted FAISS index",
    )


class StoreBootstrapConfiguration(BaseModel):
    """Paths used for seeding store data."""

    seed_csv_path: str = Field(
        default="data/regionmodel_with_detailed_descriptions.csv",
        description="CSV file used to seed SQL travel destination data",
    )


class ResolvedStoreConfiguration(BaseModel):
    """Resolved absolute paths and normalized store configs."""

    sql: SqlStoreConfiguration
    vector: VectorStoreConfiguration
    seed_csv_path: Path
    sql_db_path: Path
    vector_db_path: Path


class StoreConfiguration(BaseModel):
    """Configuration bucket for all store backends."""

    sql: SqlStoreConfiguration = Field(
        default_factory=SqlStoreConfiguration,
        description="Settings for SQL store persistence",
    )
    vector: VectorStoreConfiguration = Field(
        default_factory=VectorStoreConfiguration,
        description="Settings for vector store persistence",
    )
    bootstrap: StoreBootstrapConfiguration = Field(
        default_factory=StoreBootstrapConfiguration,
        description="Store bootstrap and migration paths",
    )

class Configuration(BaseSettings):
    '''
    Configuration settings for the recommender application.
    '''
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    env: Environment = Field(Environment.development, description="The environment the application is running in")
    log_level: LogLevel = Field(LogLevel.info, description="The logging level for the application")
    stores: StoreConfiguration = Field(
        default_factory=StoreConfiguration,
        description="Configuration for SQL and vector stores",
    )
