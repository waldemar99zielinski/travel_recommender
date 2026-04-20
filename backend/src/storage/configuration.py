from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field

DEFAULT_EMBEDDING_DIMENSION = 768
DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"


class StorageEngineConfiguration(BaseModel):
    """Database engine settings for PostgreSQL-backed storage."""

    db_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/recommender",
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


class PgVectorConfiguration(BaseModel):
    """pgvector tuning and embedding shape settings."""

    embedding_dimension: int = Field(
        default=DEFAULT_EMBEDDING_DIMENSION,
        ge=1,
        description="Embedding vector dimension used by vector similarity search",
    )
    embedding_model: str = Field(
        default=DEFAULT_EMBEDDING_MODEL,
        min_length=1,
        description="Default embedding model identifier used for vector generation",
    )


class StorageConfiguration(BaseModel):
    """Top-level storage configuration."""

    engine: StorageEngineConfiguration = Field(default_factory=StorageEngineConfiguration)
    migrations: MigrationConfiguration = Field(default_factory=MigrationConfiguration)
    vector: PgVectorConfiguration = Field(default_factory=PgVectorConfiguration)
