from __future__ import annotations

import argparse

from travel_destination_population.paths import ensure_src_path

ensure_src_path()

from storage.configuration import MigrationConfiguration
from storage.configuration import StorageConfiguration
from storage.configuration import StorageEngineConfiguration
from storage.configuration import load_storage_configuration


def build_storage_configuration(args: argparse.Namespace) -> StorageConfiguration:
    """Load runtime storage settings and apply CLI overrides."""
    runtime_configuration = load_storage_configuration()

    migrations_enabled = runtime_configuration.migrations.enabled
    if args.skip_migrations:
        migrations_enabled = False

    return StorageConfiguration(
        engine=StorageEngineConfiguration(
            db_url=args.db_url or runtime_configuration.engine.db_url,
            echo=runtime_configuration.engine.echo,
            pool_pre_ping=runtime_configuration.engine.pool_pre_ping,
            pool_size=runtime_configuration.engine.pool_size,
            max_overflow=runtime_configuration.engine.max_overflow,
        ),
        migrations=MigrationConfiguration(
            enabled=migrations_enabled,
            lock_key=runtime_configuration.migrations.lock_key,
        ),
        schema_name=args.schema_name or runtime_configuration.schema_name,
    )
