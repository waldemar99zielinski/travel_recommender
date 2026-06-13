from __future__ import annotations

import argparse
from pathlib import Path

from travel_destination_population.loader import populate_travel_destination_store
from travel_destination_population.paths import resolve_default_csv_path
from travel_destination_population.runtime import build_embedding_configuration
from travel_destination_population.runtime import build_storage_configuration


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for CSV-to-PostgreSQL destination population."""
    parser = argparse.ArgumentParser(
        description="Populate travel_destinations in PostgreSQL from CSV and generate embeddings for descriptions.",
    )
    parser.add_argument(
        "--csv-path",
        type=Path,
        default=resolve_default_csv_path(),
        help="CSV file containing travel destination descriptions and metadata.",
    )
    parser.add_argument(
        "--db-url",
        type=str,
        default=None,
        help="Optional PostgreSQL SQLAlchemy URL override. Defaults to STORAGE_ENGINE__DB_URL from backend/.env.",
    )
    parser.add_argument(
        "--schema-name",
        type=str,
        default=None,
        help="Optional PostgreSQL schema override. Defaults to STORAGE_SCHEMA_NAME from backend/.env.",
    )
    parser.add_argument(
        "--skip-migrations",
        action="store_true",
        help="Skip running migrations before loading data.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=200,
        help="Batch size for store upsert operations.",
    )
    parser.add_argument(
        "--embeddings-provider",
        type=str,
        choices=("ollama", "openai"),
        default=None,
        help="Optional embedding provider override. Defaults to EMBEDDINGS_PROVIDER from backend/.env.",
    )
    parser.add_argument(
        "--embeddings-model-name",
        type=str,
        default=None,
        help="Optional embedding model override. Defaults to EMBEDDINGS_MODEL_NAME from backend/.env.",
    )
    parser.add_argument(
        "--embeddings-base-url",
        type=str,
        default=None,
        help="Optional embedding base URL override. Defaults to EMBEDDINGS_BASE_URL from backend/.env.",
    )
    parser.add_argument(
        "--no-embeddings-base-url",
        action="store_true",
        help="Clear EMBEDDINGS_BASE_URL and use the provider default endpoint.",
    )
    parser.add_argument(
        "--embeddings-api-key",
        type=str,
        default=None,
        help="Optional embedding API key override. Defaults to EMBEDDINGS_API_KEY from backend/.env.",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    """Validate CLI arguments before starting the load."""
    if args.batch_size <= 0:
        raise ValueError("--batch-size must be greater than zero")
    if not args.csv_path.exists():
        raise FileNotFoundError(f"Travel destination CSV file not found: {args.csv_path}")
    if args.embeddings_model_name is not None and not args.embeddings_model_name.strip():
        raise ValueError("--embeddings-model-name must not be empty")
    if args.no_embeddings_base_url and args.embeddings_base_url is not None:
        raise ValueError("Use either --embeddings-base-url or --no-embeddings-base-url, not both")
    if args.embeddings_api_key is not None and not args.embeddings_api_key.strip():
        raise ValueError("--embeddings-api-key must not be empty")


def main() -> None:
    """Run CSV-driven population into PostgreSQL-backed travel destination storage."""
    args = parse_args()
    validate_args(args)

    storage_configuration = build_storage_configuration(args)
    embedding_configuration = build_embedding_configuration(args)
    print(f"Using storage configuration: {storage_configuration}")
    print(f"Using embedding configuration: {embedding_configuration}")
    inserted_rows = populate_travel_destination_store(
        csv_path=args.csv_path,
        storage_configuration=storage_configuration,
        embedding_configuration=embedding_configuration,
        batch_size=args.batch_size,
    )

    print(f"Populated {inserted_rows} travel destination row(s) from {args.csv_path}")
