from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.engine import Engine

from utils.logger import LoggerManager


@dataclass(frozen=True, slots=True)
class MigrationStep:
    """Represents one idempotent SQL migration step."""

    version: int
    description: str
    statements: tuple[str, ...]


MIGRATIONS_DIRECTORY = Path(__file__).resolve().parent / "migrations"
MIN_POSTGRESQL_SERVER_VERSION_NUM = 180000
MIN_PGVECTOR_EXTENSION_VERSION = (0, 5, 0)

logger = LoggerManager.get_logger(__name__)


def run_storage_migrations(
    engine: Engine,
    *,
    embedding_dimension: int,
    migration_lock_key: int,
) -> None:
    """Apply storage migrations with advisory locking and schema contract checks."""
    if embedding_dimension <= 0:
        raise ValueError("embedding_dimension must be greater than zero")

    logger.info(
        "Starting storage migrations (embedding_dimension=%s, lock_key=%s)",
        embedding_dimension,
        migration_lock_key,
    )

    migration_steps = _load_ordered_migration_steps(embedding_dimension=embedding_dimension)
    logger.info("Loaded %s storage migration step(s)", len(migration_steps))

    with engine.begin() as connection:
        _validate_postgresql_compatibility(connection)
        logger.info("PostgreSQL compatibility check passed")

        connection.execute(text("SELECT pg_advisory_xact_lock(:lock_key)"), {"lock_key": migration_lock_key})
        logger.info("Acquired storage migration advisory lock")
        _ensure_migrations_table(connection)
        applied_versions = _fetch_applied_versions(connection)
        logger.info("Found %s already-applied migration(s)", len(applied_versions))

        applied_now = 0
        skipped = 0

        for step in migration_steps:
            if step.version in applied_versions:
                skipped += 1
                logger.debug(
                    "Skipping already-applied migration version=%s description=%s",
                    step.version,
                    step.description,
                )
                continue

            logger.info(
                "Applying migration version=%s description=%s",
                step.version,
                step.description,
            )

            for statement in step.statements:
                connection.execute(text(statement))

            connection.execute(
                text(
                    """
                    INSERT INTO storage_schema_migrations (version, description)
                    VALUES (:version, :description)
                    """
                ),
                {
                    "version": step.version,
                    "description": step.description,
                },
            )
            applied_now += 1
            logger.info("Applied migration version=%s", step.version)

        _validate_vector_extension_compatibility(connection)
        logger.info("pgvector extension compatibility check passed")
        _validate_embedding_dimension_contract(connection, expected_embedding_dimension=embedding_dimension)
        logger.info("Embedding dimension contract validation passed")

    logger.info(
        "Storage migrations completed (applied=%s, skipped=%s)",
        applied_now,
        skipped,
    )


def validate_storage_contract(engine: Engine, *, embedding_dimension: int) -> None:
    """Validate that runtime embedding settings match persisted storage metadata."""
    logger.info("Validating storage contract (embedding_dimension=%s)", embedding_dimension)
    with engine.connect() as connection:
        _validate_postgresql_compatibility(connection)
        _validate_vector_extension_compatibility(connection)
        _validate_embedding_dimension_contract(
            connection,
            expected_embedding_dimension=embedding_dimension,
        )
    logger.info("Storage contract validation passed")


def _load_ordered_migration_steps(embedding_dimension: int) -> tuple[MigrationStep, ...]:
    migration_files = sorted(MIGRATIONS_DIRECTORY.glob("*.sql"))
    if not migration_files:
        raise RuntimeError(f"No SQL migration files found in {MIGRATIONS_DIRECTORY}")

    logger.debug("Discovered %s migration file(s) in %s", len(migration_files), MIGRATIONS_DIRECTORY)

    migration_steps: list[MigrationStep] = []
    seen_versions: set[int] = set()

    for migration_file in migration_files:
        version, description = _parse_migration_filename(migration_file)
        if version in seen_versions:
            raise RuntimeError(f"Duplicate migration version detected: {version}")
        seen_versions.add(version)

        sql_template = migration_file.read_text(encoding="utf-8")
        sql_statement = sql_template.replace("{{embedding_dimension}}", str(embedding_dimension)).strip()
        if not sql_statement:
            raise RuntimeError(f"Migration file is empty: {migration_file}")

        migration_steps.append(
            MigrationStep(
                version=version,
                description=description,
                statements=(sql_statement,),
            )
        )
        logger.debug("Prepared migration step version=%s description=%s", version, description)

    return tuple(migration_steps)


def _parse_migration_filename(migration_file: Path) -> tuple[int, str]:
    file_stem = migration_file.stem
    version_text, separator, description_text = file_stem.partition("__")
    if not separator or not version_text or not description_text:
        raise RuntimeError(
            "Migration filenames must follow '<version>__<description>.sql'. "
            f"Invalid filename: {migration_file.name}"
        )

    if not version_text.isdigit():
        raise RuntimeError(f"Migration version must be numeric: {migration_file.name}")

    version = int(version_text)
    description = description_text.replace("_", " ").strip()
    if not description:
        raise RuntimeError(f"Migration description is empty: {migration_file.name}")

    return version, description


def _validate_postgresql_compatibility(connection: Connection) -> None:
    server_version_num = int(connection.execute(text("SHOW server_version_num")).scalar_one())
    logger.debug("Detected PostgreSQL server_version_num=%s", server_version_num)
    if server_version_num < MIN_POSTGRESQL_SERVER_VERSION_NUM:
        raise RuntimeError(
            "Storage requires PostgreSQL 18 or newer. "
            f"Detected server_version_num={server_version_num}."
        )


def _validate_vector_extension_compatibility(connection: Connection) -> None:
    installed_version = connection.execute(
        text(
            """
            SELECT installed_version
            FROM pg_available_extensions
            WHERE name = 'vector'
            """
        )
    ).scalar_one_or_none()

    if installed_version is None:
        raise RuntimeError(
            "pgvector extension is not available in this PostgreSQL 18 installation. "
            "Install pgvector built for PostgreSQL 18."
        )

    version_tuple = _parse_extension_version(str(installed_version))
    logger.debug("Detected pgvector extension version=%s", installed_version)
    if version_tuple < MIN_PGVECTOR_EXTENSION_VERSION:
        required = ".".join(str(part) for part in MIN_PGVECTOR_EXTENSION_VERSION)
        raise RuntimeError(
            "pgvector extension version is too old for required features. "
            f"Detected={installed_version}, required>={required}."
        )


def _parse_extension_version(version: str) -> tuple[int, int, int]:
    match = re.match(r"^(\d+)\.(\d+)(?:\.(\d+))?", version)
    if match is None:
        raise RuntimeError(f"Unable to parse extension version: {version}")

    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3) or 0)
    return (major, minor, patch)


def _ensure_migrations_table(connection: Connection) -> None:
    logger.debug("Ensuring storage_schema_migrations table exists")
    connection.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS storage_schema_migrations (
                version INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )


def _fetch_applied_versions(connection: Connection) -> set[int]:
    rows = connection.execute(text("SELECT version FROM storage_schema_migrations")).all()
    return {int(version) for (version,) in rows}


def _validate_embedding_dimension_contract(
    connection: Connection,
    expected_embedding_dimension: int,
) -> None:
    result = connection.execute(
        text("SELECT value FROM storage_metadata WHERE key = 'embedding_dimension'")
    ).one_or_none()

    if result is None:
        raise RuntimeError("Storage metadata missing `embedding_dimension` contract.")

    actual_embedding_dimension = int(result[0])
    logger.debug(
        "Embedding dimension contract values expected=%s actual=%s",
        expected_embedding_dimension,
        actual_embedding_dimension,
    )
    if actual_embedding_dimension != expected_embedding_dimension:
        raise RuntimeError(
            "Configured embedding dimension does not match database contract: "
            f"expected={expected_embedding_dimension}, actual={actual_embedding_dimension}."
        )
