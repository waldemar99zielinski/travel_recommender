from __future__ import annotations

import argparse

from travel_destination_population.paths import ensure_src_path

ensure_src_path()

from embeddings.configuration import TextEmbeddingModelConfiguration
from embeddings.configuration import load_text_embedding_model_configuration
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


def build_embedding_configuration(args: argparse.Namespace) -> TextEmbeddingModelConfiguration:
    """Load runtime embedding settings and apply CLI overrides."""
    runtime_configuration = load_text_embedding_model_configuration()

    base_url = runtime_configuration.base_url
    if args.no_embeddings_base_url:
        base_url = None
    elif args.embeddings_base_url is not None:
        normalized_base_url = args.embeddings_base_url.strip()
        base_url = normalized_base_url or None

    return TextEmbeddingModelConfiguration(
        provider=args.embeddings_provider if args.embeddings_provider is not None else runtime_configuration.provider,
        model_name=args.embeddings_model_name if args.embeddings_model_name is not None else runtime_configuration.model_name,
        base_url=base_url,
        api_key=args.embeddings_api_key if args.embeddings_api_key is not None else runtime_configuration.api_key,
    )
