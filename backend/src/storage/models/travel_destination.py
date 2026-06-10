from __future__ import annotations

from datetime import datetime
from datetime import timezone

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import func
from sqlalchemy import text
from sqlmodel import Field
from sqlmodel import SQLModel

from storage.models.vector_type import create_vector_column


class TravelDestinationRecord(SQLModel, table=True):
    """Unified PostgreSQL record for metadata and vector embedding search."""

    __tablename__ = "travel_destinations"

    id: str = Field(primary_key=True)
    parent_region: str
    region: str

    popularity: float
    cost_per_week: float

    jan: float
    feb: float
    mar: float
    apr: float
    may: float
    jun: float
    jul: float
    aug: float
    sep: float
    oct: float
    nov: float
    dec: float

    nature: float
    hiking: float
    beach: float
    watersports: float
    entertainment: float
    wintersports: float
    culture: float
    culinary: float
    architecture: float
    shopping: float

    description: str
    embedding: list[float] = Field(
        sa_column=create_vector_column(nullable=False),
    )
    embedding_version: int = Field(default=1, ge=1)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            onupdate=func.now(),
        ),
    )
