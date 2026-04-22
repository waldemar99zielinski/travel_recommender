from __future__ import annotations

from collections.abc import Sequence

from storage.db.unit_of_work import StorageUnitOfWork
from storage.models.storage_metadata import StorageMetadataRecord
from storage.repositories.storage_metadata_repository import StorageMetadataRepository


class StorageMetadataStore:
    """Store facade for storage metadata key-value records."""

    def __init__(self, unit_of_work: StorageUnitOfWork) -> None:
        self.unit_of_work = unit_of_work

    def list_all(self) -> list[StorageMetadataRecord]:
        """Return all metadata records."""
        with self.unit_of_work.read() as session:
            repository = StorageMetadataRepository(session)
            return repository.list_all()

    def get(self, key: str) -> StorageMetadataRecord | None:
        """Return metadata record by key if present."""
        with self.unit_of_work.read() as session:
            repository = StorageMetadataRepository(session)
            return repository.get(key)

    def get_value(self, key: str) -> str | None:
        """Return metadata value by key if present."""
        with self.unit_of_work.read() as session:
            repository = StorageMetadataRepository(session)
            return repository.get_value(key)

    def upsert_many(self, rows: Sequence[StorageMetadataRecord]) -> None:
        """Insert or update many metadata records by key."""
        with self.unit_of_work.write() as session:
            repository = StorageMetadataRepository(session)
            repository.upsert_many(rows)

    def upsert(self, key: str, value: str) -> None:
        """Insert or update one metadata key-value pair."""
        with self.unit_of_work.write() as session:
            repository = StorageMetadataRepository(session)
            repository.upsert(key, value)

    def delete(self, key: str) -> None:
        """Delete metadata key-value pair by key."""
        with self.unit_of_work.write() as session:
            repository = StorageMetadataRepository(session)
            repository.delete(key)
