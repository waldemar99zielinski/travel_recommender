from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session
from sqlmodel import col
from sqlmodel import delete
from sqlmodel import select

from storage.models.storage_metadata import StorageMetadataRecord


class StorageMetadataRepository:
    """Repository for storage metadata key-value records."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[StorageMetadataRecord]:
        """Return all metadata records."""
        statement = select(StorageMetadataRecord).order_by(col(StorageMetadataRecord.key))
        return list(self.session.exec(statement).all())

    def get(self, key: str) -> StorageMetadataRecord | None:
        """Return metadata record by key if present."""
        statement = select(StorageMetadataRecord).where(col(StorageMetadataRecord.key) == key)
        return self.session.exec(statement).first()

    def get_value(self, key: str) -> str | None:
        """Return metadata value by key if present."""
        record = self.get(key)
        if record is None:
            return None
        return record.value

    def upsert_many(self, rows: Sequence[StorageMetadataRecord]) -> None:
        """Insert or update many metadata records by key."""
        if not rows:
            return

        payloads = [row.model_dump(exclude_none=True) for row in rows]
        statement = insert(StorageMetadataRecord).values(payloads)
        updatable_columns = {
            field_name: getattr(statement.excluded, field_name)
            for field_name in payloads[0]
            if field_name != "key"
        }

        upsert_statement = statement.on_conflict_do_update(
            index_elements=["key"],
            set_=updatable_columns,
        )
        self.session.exec(upsert_statement)

    def upsert(self, key: str, value: str) -> None:
        """Insert or update a metadata key-value pair."""
        self.upsert_many([StorageMetadataRecord(key=key, value=value)])

    def delete(self, key: str) -> None:
        """Delete metadata key-value pair by key."""
        statement = delete(StorageMetadataRecord).where(col(StorageMetadataRecord.key) == key)
        self.session.exec(statement)
