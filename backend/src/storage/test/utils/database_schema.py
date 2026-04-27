from __future__ import annotations

import re
from urllib.parse import parse_qsl
from urllib.parse import quote_plus
from urllib.parse import urlencode
from urllib.parse import urlparse
from urllib.parse import urlunparse
from uuid import uuid4

from sqlalchemy import text
from sqlmodel import create_engine

SCHEMA_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def generate_schema_name(prefix: str = "test_storage_bootstrap") -> str:
    """Create a safe, random PostgreSQL schema name for tests."""
    return f"{prefix}_{uuid4().hex[:12]}"


def build_db_url_with_schema_search_path(base_db_url: str, schema_name: str) -> str:
    """Attach search_path option to a SQLAlchemy PostgreSQL URL."""
    parsed = urlparse(base_db_url)
    query_params = dict(parse_qsl(parsed.query, keep_blank_values=True))

    search_path_option = f"-csearch_path={schema_name},public"
    existing_options = query_params.get("options")
    query_params["options"] = f"{existing_options} {search_path_option}" if existing_options else search_path_option

    encoded_query = urlencode(query_params, quote_via=quote_plus)
    return urlunparse(parsed._replace(query=encoded_query))


def create_schema(base_db_url: str, schema_name: str) -> None:
    """Create test schema if it does not exist."""
    quoted_schema_name = _quote_schema_name(schema_name)
    engine = create_engine(base_db_url)
    try:
        with engine.begin() as connection:
            connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {quoted_schema_name}"))
    finally:
        engine.dispose()


def drop_schema(base_db_url: str, schema_name: str) -> None:
    """Drop test schema and all nested objects."""
    quoted_schema_name = _quote_schema_name(schema_name)
    engine = create_engine(base_db_url)
    try:
        with engine.begin() as connection:
            connection.execute(text(f"DROP SCHEMA IF EXISTS {quoted_schema_name} CASCADE"))
    finally:
        engine.dispose()


def count_persisted_destinations(db_url: str) -> int:
    """Count travel_destinations rows in selected search_path schema."""
    engine = create_engine(db_url)
    try:
        with engine.connect() as connection:
            return int(connection.execute(text("SELECT COUNT(*) FROM travel_destinations")).scalar_one())
    finally:
        engine.dispose()


def load_persisted_destination_ids(db_url: str) -> set[str]:
    """Load all persisted travel destination IDs in selected search_path schema."""
    engine = create_engine(db_url)
    try:
        with engine.connect() as connection:
            rows = connection.execute(text("SELECT id FROM travel_destinations")).all()
            return {str(row[0]) for row in rows}
    finally:
        engine.dispose()


def _quote_schema_name(schema_name: str) -> str:
    if SCHEMA_NAME_PATTERN.fullmatch(schema_name) is None:
        raise ValueError(f"Invalid schema name: {schema_name}")
    return f'"{schema_name}"'
