from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.engine import Engine

from storage.db.migration_runner import MIN_POSTGRESQL_SERVER_VERSION_NUM
from storage.db.migration_runner import MIN_PGVECTOR_EXTENSION_VERSION


@dataclass(frozen=True, slots=True)
class StorageHealthReport:
    """Health report for PostgreSQL + pgvector storage."""

    is_healthy: bool
    database_reachable: bool
    postgresql_18_compatible: bool
    pgvector_enabled: bool
    pgvector_version_compatible: bool
    embedding_dimension_matches: bool
    vector_index_present: bool
    details: str


def check_storage_health(engine: Engine, expected_embedding_dimension: int) -> StorageHealthReport:
    """Run a lightweight storage health check suite."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

            server_version_num = int(connection.execute(text("SHOW server_version_num")).scalar_one())
            postgresql_18_compatible = server_version_num >= MIN_POSTGRESQL_SERVER_VERSION_NUM

            pgvector_installed = connection.execute(
                text("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector')")
            ).scalar_one()

            installed_vector_version = connection.execute(
                text(
                    """
                    SELECT installed_version
                    FROM pg_available_extensions
                    WHERE name = 'vector'
                    """
                )
            ).scalar_one_or_none()
            pgvector_version_compatible = bool(
                installed_vector_version is not None
                and _is_vector_version_compatible(str(installed_vector_version))
            )

            embedding_dimension_value = connection.execute(
                text("SELECT value FROM storage_metadata WHERE key = 'embedding_dimension'")
            ).scalar_one_or_none()
            embedding_dimension_matches = (
                embedding_dimension_value is not None
                and int(embedding_dimension_value) == expected_embedding_dimension
            )

            vector_index_present = connection.execute(
                text(
                    """
                    SELECT EXISTS (
                        SELECT 1
                        FROM pg_indexes
                        WHERE schemaname = 'public'
                          AND tablename = 'travel_destinations'
                          AND indexname = 'ix_travel_destinations_embedding_hnsw'
                    )
                    """
                )
            ).scalar_one()

    except Exception as error:
        return StorageHealthReport(
            is_healthy=False,
            database_reachable=False,
            postgresql_18_compatible=False,
            pgvector_enabled=False,
            pgvector_version_compatible=False,
            embedding_dimension_matches=False,
            vector_index_present=False,
            details=f"Storage health check failed: {error}",
        )

    is_healthy = bool(
        postgresql_18_compatible
        and pgvector_installed
        and pgvector_version_compatible
        and embedding_dimension_matches
        and vector_index_present
    )
    details = "ok" if is_healthy else "Storage checks reported one or more failing indicators"

    return StorageHealthReport(
        is_healthy=is_healthy,
        database_reachable=True,
        postgresql_18_compatible=postgresql_18_compatible,
        pgvector_enabled=bool(pgvector_installed),
        pgvector_version_compatible=pgvector_version_compatible,
        embedding_dimension_matches=bool(embedding_dimension_matches),
        vector_index_present=bool(vector_index_present),
        details=details,
    )


def _is_vector_version_compatible(version: str) -> bool:
    parts = version.split(".")
    if len(parts) < 2:
        return False

    try:
        major = int(parts[0])
        minor = int(parts[1])
        patch = int(parts[2]) if len(parts) >= 3 else 0
    except ValueError:
        return False

    return (major, minor, patch) >= MIN_PGVECTOR_EXTENSION_VERSION
