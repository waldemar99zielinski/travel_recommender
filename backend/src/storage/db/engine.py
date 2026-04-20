from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlmodel import create_engine

from storage.configuration import StorageEngineConfiguration


def create_storage_engine(config: StorageEngineConfiguration) -> Engine:
    """Create a SQLAlchemy engine for PostgreSQL storage."""
    if not config.db_url.startswith("postgresql+") and not config.db_url.startswith("postgresql://"):
        raise ValueError("Storage engine requires a PostgreSQL SQLAlchemy URL.")

    return create_engine(
        config.db_url,
        echo=config.echo,
        pool_pre_ping=config.pool_pre_ping,
        pool_size=config.pool_size,
        max_overflow=config.max_overflow,
    )


def ensure_pgvector_extension(engine: Engine) -> None:
    """Ensure pgvector extension exists in the current database."""
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
