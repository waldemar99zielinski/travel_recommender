from __future__ import annotations

from collections.abc import Sequence

from storage.db.unit_of_work import StorageUnitOfWork
from storage.models.travel_destination import TravelDestinationRecord
from storage.repositories.travel_destination_repository import TravelDestinationRepository


def seed_travel_destinations(
    unit_of_work: StorageUnitOfWork,
    rows: Sequence[TravelDestinationRecord],
    *,
    embedding_dimension: int,
    batch_size: int = 500,
) -> int:
    """Bulk seed travel destinations in batches using UPSERT semantics."""
    if embedding_dimension <= 0:
        raise ValueError("embedding_dimension must be greater than zero")
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero")

    total_rows = len(rows)
    if total_rows == 0:
        return 0

    for start_index in range(0, total_rows, batch_size):
        end_index = min(start_index + batch_size, total_rows)
        batch = rows[start_index:end_index]

        with unit_of_work.write() as session:
            repository = TravelDestinationRepository(
                session,
                embedding_dimension=embedding_dimension,
            )
            repository.upsert_many(batch)

    return total_rows
