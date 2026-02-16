from __future__ import annotations

from sqlmodel import Field
from sqlmodel import SQLModel


class TravelDestinationTable(SQLModel, table=True):
    """SQLModel table for normalized travel destination data."""

    id: str = Field(primary_key=True)  # Corresponds to CSV field `u_name`.
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

    safety: float
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
