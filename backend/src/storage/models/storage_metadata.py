from __future__ import annotations

from datetime import UTC
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import text
from sqlmodel import Field
from sqlmodel import SQLModel


class StorageMetadataRecord(SQLModel, table=True):
    """Metadata key-value record for storage runtime contracts."""

    __tablename__ = "storage_metadata"

    key: str = Field(primary_key=True)
    value: str
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
    )
