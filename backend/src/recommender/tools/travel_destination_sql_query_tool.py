from __future__ import annotations

import json
import re
from datetime import date
from datetime import datetime
from decimal import Decimal
from typing import Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel
from pydantic import Field
from sqlalchemy import text
from sqlalchemy.engine import Engine

from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

_READ_ONLY_PREFIXES = ("select", "with")
_FORBIDDEN_SQL_PATTERNS = (
    r"\binsert\b",
    r"\bupdate\b",
    r"\bdelete\b",
    r"\bdrop\b",
    r"\balter\b",
    r"\btruncate\b",
    r"\bcreate\b",
    r"\bgrant\b",
    r"\brevoke\b",
)


class TravelDestinationSQLQueryToolInput(BaseModel):
    """A read-only SQL query executed against the travel_destinations table."""

    sql_query: str = Field(
        ...,
        description=(
            "A read-only PostgreSQL query that targets the travel_destinations table. "
            "Use SELECT or WITH queries only."
        ),
        min_length=1,
        max_length=4000,
    )


def _normalize_sql_query(sql_query: str) -> str:
    normalized = sql_query.strip()
    if not normalized:
        raise ValueError("sql_query must not be empty")

    lower_query = normalized.lower()
    if not lower_query.startswith(_READ_ONLY_PREFIXES):
        raise ValueError("sql_query must start with SELECT or WITH")

    if lower_query.count(";") > 1 or (";" in lower_query[:-1]):
        raise ValueError("sql_query must contain at most one trailing semicolon")

    for pattern in _FORBIDDEN_SQL_PATTERNS:
        if re.search(pattern, lower_query):
            raise ValueError("sql_query must be read-only")

    if "travel_destinations" not in lower_query:
        raise ValueError("sql_query must reference the travel_destinations table")

    order_by_index = lower_query.find(" order by ")
    limit_index = lower_query.find(" limit ")
    if order_by_index != -1 and limit_index != -1 and limit_index < order_by_index:
        raise ValueError("sql_query must place ORDER BY before LIMIT")

    return normalized.rstrip(";")


def _serialize_value(value: object) -> object:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime | date):
        return value.isoformat()
    return value


def create_travel_destination_sql_query_tool(engine: Engine) -> StructuredTool:
    """Create a read-only SQL execution tool for the travel_destinations table."""
    if engine is None:
        raise ValueError("engine is required")

    def execute_travel_destination_sql_query(sql_query: str) -> str:
        """Execute a read-only SQL query against the travel_destinations table."""
        logger.info("execute_travel_destination_sql_query called with sql_query=%s", sql_query)

        normalized_query = _normalize_sql_query(sql_query)
        logger.info("Travel destination SQL normalized query: %s", normalized_query)

        with engine.connect() as connection:
            result = connection.execute(text(normalized_query))
            rows = [
                {key: _serialize_value(value) for key, value in row.items()}
                for row in result.mappings().all()
            ]

        logger.info("Travel destination SQL returned %d rows: %s", len(rows), rows)
        return json.dumps(rows)

    return StructuredTool.from_function(
        func=execute_travel_destination_sql_query,
        name="execute_travel_destination_sql_query",
        args_schema=TravelDestinationSQLQueryToolInput,
        description=(
            "Execute a read-only PostgreSQL query against the travel_destinations table "
            "and return the result rows as JSON."
        ),
    )
