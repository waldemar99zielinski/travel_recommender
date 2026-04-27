from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Sequence

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.engine import Engine

MIN_POSTGRESQL_SERVER_VERSION_NUM = 180000
MIN_PGVECTOR_EXTENSION_VERSION = (0, 5, 0)


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


def check_storage_health(
    engine: Engine,
    expected_embedding_dimension: int,
    *,
    schema_name: str,
) -> StorageHealthReport:
    """Run a lightweight storage health check suite."""
    try:
        with engine.connect() as connection:
            database_reachable, database_failure_message = _check_database_reachable(connection)
            if not database_reachable:
                return StorageHealthReport(
                    is_healthy=False,
                    database_reachable=False,
                    postgresql_18_compatible=False,
                    pgvector_enabled=False,
                    pgvector_version_compatible=False,
                    embedding_dimension_matches=False,
                    vector_index_present=False,
                    details=_build_health_details(
                        is_healthy=False,
                        failure_messages=[database_failure_message],
                    ),
                )

            postgresql_18_compatible, postgresql_failure_message = _check_postgresql_compatibility(connection)
            pgvector_enabled, pgvector_enabled_failure_message = _check_pgvector_enabled(connection)
            pgvector_version_compatible, pgvector_version_failure_message = _check_pgvector_version_compatibility(
                connection
            )
            embedding_dimension_matches, embedding_dimension_failure_message = _check_embedding_dimension_contract(
                connection,
                expected_embedding_dimension=expected_embedding_dimension,
            )
            vector_index_present, vector_index_failure_message = _check_vector_index_present(
                connection,
                schema_name=schema_name,
            )

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
        and pgvector_enabled
        and pgvector_version_compatible
        and embedding_dimension_matches
        and vector_index_present
    )

    details = _build_health_details(
        is_healthy=is_healthy,
        failure_messages=_collect_failure_messages(
            (
                postgresql_failure_message,
                pgvector_enabled_failure_message,
                pgvector_version_failure_message,
                embedding_dimension_failure_message,
                vector_index_failure_message,
            )
        ),
    )

    return StorageHealthReport(
        is_healthy=is_healthy,
        database_reachable=True,
        postgresql_18_compatible=postgresql_18_compatible,
        pgvector_enabled=pgvector_enabled,
        pgvector_version_compatible=pgvector_version_compatible,
        embedding_dimension_matches=embedding_dimension_matches,
        vector_index_present=vector_index_present,
        details=details,
    )


def validate_storage_health(
    engine: Engine,
    *,
    expected_embedding_dimension: int,
    schema_name: str,
) -> None:
    """Raise when storage health checks fail for the expected embedding contract."""
    report = check_storage_health(
        engine,
        expected_embedding_dimension=expected_embedding_dimension,
        schema_name=schema_name,
    )
    if not report.is_healthy:
        raise RuntimeError(report.details)


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


def _build_health_details(*, is_healthy: bool, failure_messages: Sequence[str]) -> str:
    if is_healthy:
        return "ok"

    if not failure_messages:
        return "Storage health check failed: unknown reason"

    return "Storage health check failed: " + ", ".join(failure_messages)


def _collect_failure_messages(messages: Sequence[str | None]) -> list[str]:
    return [message for message in messages if message is not None]


def _check_database_reachable(connection: Connection) -> tuple[bool, str | None]:
    try:
        connection.execute(text("SELECT 1"))
    except Exception as error:
        return False, f"database_reachable=false (failed to execute ping query: {error})"

    return True, None


def _check_postgresql_compatibility(connection: Connection) -> tuple[bool, str | None]:
    try:
        server_version_num = int(connection.execute(text("SHOW server_version_num")).scalar_one())
    except Exception as error:
        return False, f"postgresql_18_compatible=false (failed to read server version: {error})"

    if server_version_num < MIN_POSTGRESQL_SERVER_VERSION_NUM:
        return (
            False,
            "postgresql_18_compatible=false "
            f"(server_version_num={server_version_num}, required>={MIN_POSTGRESQL_SERVER_VERSION_NUM})",
        )

    return True, None


def _check_pgvector_enabled(connection: Connection) -> tuple[bool, str | None]:
    try:
        pgvector_installed = bool(
            connection.execute(
                text("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector')")
            ).scalar_one()
        )
    except Exception as error:
        return False, f"pgvector_enabled=false (failed to query extension status: {error})"

    if not pgvector_installed:
        return False, "pgvector_enabled=false (extension `vector` not installed)"

    return True, None


def _check_pgvector_version_compatibility(connection: Connection) -> tuple[bool, str | None]:
    required_pgvector_version = _format_version(MIN_PGVECTOR_EXTENSION_VERSION)

    try:
        installed_vector_version = connection.execute(
            text(
                """
                SELECT installed_version
                FROM pg_available_extensions
                WHERE name = 'vector'
                """
            )
        ).scalar_one_or_none()
    except Exception as error:
        return False, f"pgvector_version_compatible=false (failed to query extension version: {error})"

    if installed_vector_version is None:
        return (
            False,
            "pgvector_version_compatible=false "
            f"(installed=None, required>={required_pgvector_version})",
        )

    installed_vector_version_text = str(installed_vector_version)
    if not _is_vector_version_compatible(installed_vector_version_text):
        return (
            False,
            "pgvector_version_compatible=false "
            f"(installed={installed_vector_version_text!r}, required>={required_pgvector_version})",
        )

    return True, None


def _check_embedding_dimension_contract(
    connection: Connection,
    *,
    expected_embedding_dimension: int,
) -> tuple[bool, str | None]:
    try:
        raw_embedding_dimension_value = connection.execute(
            text("SELECT value FROM storage_metadata WHERE key = 'embedding_dimension'")
        ).scalar_one_or_none()
    except Exception as error:
        return False, f"embedding_dimension_matches=false (failed to query storage metadata: {error})"

    if raw_embedding_dimension_value is None:
        return (
            False,
            "embedding_dimension_matches=false "
            f"(storage_metadata key missing, expected={expected_embedding_dimension})",
        )

    try:
        actual_embedding_dimension = int(raw_embedding_dimension_value)
    except (TypeError, ValueError):
        return (
            False,
            "embedding_dimension_matches=false "
            "(storage_metadata.embedding_dimension is not an integer "
            f"value={raw_embedding_dimension_value!r}, expected={expected_embedding_dimension})",
        )

    if actual_embedding_dimension != expected_embedding_dimension:
        return (
            False,
            "embedding_dimension_matches=false "
            f"(actual={actual_embedding_dimension}, expected={expected_embedding_dimension})",
        )

    return True, None


def _check_vector_index_present(connection: Connection, *, schema_name: str) -> tuple[bool, str | None]:
    try:
        vector_index_present = bool(
            connection.execute(
                text(
                    """
                    SELECT EXISTS (
                        SELECT 1
                        FROM pg_indexes
                        WHERE schemaname = :schema_name
                          AND tablename = 'travel_destinations'
                          AND indexname = 'ix_travel_destinations_embedding_hnsw'
                    )
                    """
                ),
                {"schema_name": schema_name},
            ).scalar_one()
        )
    except Exception as error:
        return False, f"vector_index_present=false (failed to query index metadata: {error})"

    if not vector_index_present:
        return (
            False,
            "vector_index_present=false "
            "(missing index `ix_travel_destinations_embedding_hnsw` "
            f"in schema={schema_name!r})",
        )

    return True, None


def _format_version(version: tuple[int, int, int]) -> str:
    return ".".join(str(part) for part in version)
