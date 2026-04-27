from __future__ import annotations

import argparse
from pathlib import Path

from embeddings.configuration import OllamaTextEmbeddingModelConfiguration
from embeddings.configuration import load_ollama_text_embedding_model_configuration
from embeddings.ollama_text_embedding_model import OllamaTextEmbeddingModel
from embeddings.protocols import TextEmbeddingModelProtocol
from storage.bootstrap.travel_destination_csv_bootstrap import (
    load_travel_destination_records_from_csv,
)
from storage.bootstrap.travel_destination_seed import seed_travel_destinations
from storage.configuration import MigrationConfiguration
from storage.configuration import StorageConfiguration
from storage.configuration import StorageEngineConfiguration
from storage.storage import Storage
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

DEFAULT_SEED_CSV_PATH = Path(__file__).resolve().parents[2] / "data" / "regionmodel_with_detailed_descriptions.csv"


def bootstrap_travel_destinations_from_csv(
    *,
    csv_file_path: Path,
    storage_configuration: StorageConfiguration,
    embedding_model: TextEmbeddingModelProtocol,
    batch_size: int,
) -> int:
    """Load travel destinations from CSV, generate embeddings, and upsert into storage."""
    logger.info("Initializing storage for bootstrap")
    storage = Storage(
        storage_configuration,
        embedding_model=embedding_model,
    )
    try:
        logger.info("Loading and embedding travel destinations from %s", csv_file_path)
        records = load_travel_destination_records_from_csv(
            csv_file_path,
            embedding_model=embedding_model,
        )

        logger.info("Prepared %s travel destination record(s) for upsert", len(records))
        inserted_rows = seed_travel_destinations(
            storage.unit_of_work,
            records,
            embedding_dimension=embedding_model.get_dimentions(),
            batch_size=batch_size,
        )

        logger.info("Bootstrap completed: upserted_rows=%s", inserted_rows)
        return inserted_rows
    finally:
        storage.close()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap travel destinations into PostgreSQL storage using CSV + Ollama embeddings.",
    )
    parser.add_argument(
        "--csv-path",
        type=Path,
        default=DEFAULT_SEED_CSV_PATH,
        help="Path to travel destination CSV seed file.",
    )
    parser.add_argument(
        "--db-url",
        type=str,
        required=True,
        help="PostgreSQL SQLAlchemy URL for target storage database.",
    )
    parser.add_argument(
        "--skip-migrations",
        action="store_true",
        help="Skip running migrations and only validate storage contract.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=200,
        help="Batch size for upsert operations.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    if args.batch_size <= 0:
        raise ValueError("--batch-size must be greater than zero")

    configuration = StorageConfiguration(
        engine=StorageEngineConfiguration(db_url=args.db_url),
        migrations=MigrationConfiguration(enabled=not args.skip_migrations),
    )

    runtime_embedding_configuration = load_ollama_text_embedding_model_configuration()
    embedding_configuration = OllamaTextEmbeddingModelConfiguration(
        model_name=runtime_embedding_configuration.model_name,
        base_url=runtime_embedding_configuration.base_url,
    )
    embedding_model = OllamaTextEmbeddingModel(embedding_configuration)

    bootstrap_travel_destinations_from_csv(
        csv_file_path=args.csv_path,
        storage_configuration=configuration,
        embedding_model=embedding_model,
        batch_size=args.batch_size,
    )


if __name__ == "__main__":
    main()
