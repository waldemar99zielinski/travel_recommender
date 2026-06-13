from __future__ import annotations

from collections.abc import Iterator
from collections.abc import Sequence
from pathlib import Path

from travel_destination_population.paths import ensure_src_path

ensure_src_path()

from embeddings.configuration import TextEmbeddingModelConfiguration
from embeddings.loader import create_text_embedding_model
from storage.bootstrap.travel_destination_csv_bootstrap import (
    load_travel_destination_records_from_csv,
)
from storage.configuration import StorageConfiguration
from storage.models.travel_destination import TravelDestinationRecord
from storage.storage import Storage


def chunk_records(
    records: Sequence[TravelDestinationRecord],
    *,
    batch_size: int,
) -> Iterator[Sequence[TravelDestinationRecord]]:
    """Yield record batches for store upserts."""
    for start_index in range(0, len(records), batch_size):
        end_index = start_index + batch_size
        yield records[start_index:end_index]


def populate_travel_destination_store(
    *,
    csv_path: Path,
    storage_configuration: StorageConfiguration,
    embedding_configuration: TextEmbeddingModelConfiguration,
    batch_size: int,
) -> int:
    """Load CSV records, generate embeddings, and upsert them through TravelDestinationStore."""
    embedding_model = create_text_embedding_model(embedding_configuration)
    storage = Storage(storage_configuration, embedding_model=embedding_model)

    try:
        records = load_travel_destination_records_from_csv(
            csv_path,
            embedding_model=embedding_model,
        )

        for batch in chunk_records(records, batch_size=batch_size):
            storage.travel_destinations.upsert_many(batch)

        return len(records)
    finally:
        storage.close()
