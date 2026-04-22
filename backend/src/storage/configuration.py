from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

class StorageEngineConfiguration(BaseModel):
    """Database engine settings for PostgreSQL-backed storage."""

    db_url: str = Field(
        ...,
        min_length=1,
        description="SQLAlchemy database URL for PostgreSQL",
    )
    echo: bool = Field(default=False, description="Enable SQLAlchemy SQL logging")
    pool_pre_ping: bool = Field(default=True, description="Check connections before reuse")
    pool_size: int = Field(default=5, ge=1, description="Connection pool size")
    max_overflow: int = Field(default=10, ge=0, description="Maximum overflow connections")


class MigrationConfiguration(BaseModel):
    """Settings controlling startup database migrations."""

    enabled: bool = Field(
        default=True,
        description="Apply storage schema migrations automatically at startup",
    )
    lock_key: int = Field(
        default=540021,
        description="PostgreSQL advisory lock key guarding migration execution",
    )


class StorageConfiguration(BaseSettings):
    """Top-level storage configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_prefix="STORAGE_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    engine: StorageEngineConfiguration = Field(...)
    migrations: MigrationConfiguration = Field(default_factory=MigrationConfiguration)


def load_storage_configuration() -> StorageConfiguration:
    """Load storage configuration from environment variables and defaults."""
    return StorageConfiguration()  # pyright: ignore[reportCallIssue]
