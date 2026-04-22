from __future__ import annotations

import importlib
from typing import Any

from sqlalchemy import Column

_PGVECTOR_IMPORT_ERROR: Exception | None = None
PgVector: Any | None = None

try:
    pgvector_sqlalchemy_module = importlib.import_module("pgvector.sqlalchemy")
    PgVector = getattr(pgvector_sqlalchemy_module, "Vector", None)
    if PgVector is None:
        raise AttributeError("Vector type missing from pgvector.sqlalchemy")
except Exception as error:
    _PGVECTOR_IMPORT_ERROR = error


def create_vector_column(dimension: int | None = None, nullable: bool = False) -> Column[Any]:
    """Create a pgvector-backed column, failing fast when dependency is missing."""
    if PgVector is None:
        raise RuntimeError(
            "pgvector dependency is required for storage models. "
            "Install package `pgvector` before importing storage models."
        ) from _PGVECTOR_IMPORT_ERROR

    return Column(PgVector(dimension), nullable=nullable)
