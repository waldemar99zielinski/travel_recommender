from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from embeddings.protocols import TextEmbeddingModelProtocol
from storage.models.travel_destination import TravelDestinationRecord
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

PREFERENCE_VALUE_MAP: dict[str, float] = {
    "--": 0.0,
    "-": 0.25,
    "o": 0.5,
    "+": 0.75,
    "++": 1.0,
}

NUMERIC_SCORE_FIELDS: tuple[str, ...] = (
    "popularity",
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
    "nature",
    "hiking",
    "beach",
    "watersports",
    "entertainment",
    "wintersports",
    "culture",
    "culinary",
    "architecture",
    "shopping",
)


def load_travel_destination_records_from_csv(
    csv_file_path: Path,
    *,
    embedding_model: TextEmbeddingModelProtocol,
) -> list[TravelDestinationRecord]:
    """Load CSV rows into TravelDestinationRecord with generated embeddings."""
    if not csv_file_path.exists():
        raise FileNotFoundError(f"Travel destination CSV file not found: {csv_file_path}")

    records: list[TravelDestinationRecord] = []
    with csv_file_path.open(mode="r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=";")

        for row in reader:
            row_number = reader.line_num
            destination_id = _normalize_optional_text(row.get("u_name"))
            if destination_id is None:
                continue

            try:
                record = _build_travel_destination_record(
                    row,
                    embedding_model=embedding_model,
                )
            except ValueError as error:
                logger.warning(
                    "Skipping invalid travel destination row %s (id=%s): %s",
                    row_number,
                    destination_id,
                    error,
                )
                continue

            records.append(record)

    return records


def _build_travel_destination_record(
    raw_row: dict[str, str],
    *,
    embedding_model: TextEmbeddingModelProtocol,
) -> TravelDestinationRecord:
    row = _normalize_row(raw_row)

    destination_id = _require_text(row, field_name="u_name")
    parent_region = _require_text(row, field_name="parent_region")
    region = _require_text(row, field_name="region")
    description = row.get("description") or f"{region} in {parent_region}"
    cost_per_week = _parse_float(row.get("cost_per_week"), field_name="cost_per_week")

    score_values = {
        field_name: _parse_score_value(row.get(field_name), field_name=field_name)
        for field_name in NUMERIC_SCORE_FIELDS
    }

    embedding_text = _build_embedding_text(
        parent_region=parent_region,
        region=region,
        description=description,
    )
    embedding = embedding_model.embed_query(embedding_text)
    expected_embedding_dimension = embedding_model.get_dimentions()
    if len(embedding) != expected_embedding_dimension:
        raise ValueError(
            "Embedding dimension mismatch for destination "
            f"{destination_id}: expected {expected_embedding_dimension}, got {len(embedding)}"
        )

    return TravelDestinationRecord(
        id=destination_id,
        parent_region=parent_region,
        region=region,
        popularity=score_values["popularity"],
        cost_per_week=cost_per_week,
        jan=score_values["jan"],
        feb=score_values["feb"],
        mar=score_values["mar"],
        apr=score_values["apr"],
        may=score_values["may"],
        jun=score_values["jun"],
        jul=score_values["jul"],
        aug=score_values["aug"],
        sep=score_values["sep"],
        oct=score_values["oct"],
        nov=score_values["nov"],
        dec=score_values["dec"],
        nature=score_values["nature"],
        hiking=score_values["hiking"],
        beach=score_values["beach"],
        watersports=score_values["watersports"],
        entertainment=score_values["entertainment"],
        wintersports=score_values["wintersports"],
        culture=score_values["culture"],
        culinary=score_values["culinary"],
        architecture=score_values["architecture"],
        shopping=score_values["shopping"],
        description=description,
        embedding=embedding,
        embedding_version=1,
    )


def _build_embedding_text(*, parent_region: str, region: str, description: str) -> str:
    return (
        f"Destination: {region}. "
        f"Parent region: {parent_region}. "
        f"Overview: {description}"
    )


def _normalize_row(raw_row: dict[str, str]) -> dict[str, str]:
    normalized_row: dict[str, str] = {}
    for key, value in raw_row.items():
        normalized_value = _normalize_optional_text(value)
        if normalized_value is not None:
            normalized_row[key] = normalized_value
    return normalized_row


def _normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None

    normalized = str(value).strip()
    return normalized if normalized else None


def _require_text(row: dict[str, str], *, field_name: str) -> str:
    value = row.get(field_name)
    if value is None:
        raise ValueError(f"Missing required field `{field_name}`")
    return value


def _parse_score_value(value: str | None, *, field_name: str) -> float:
    if value is None:
        raise ValueError(f"Missing required score field `{field_name}`")

    mapped_value = PREFERENCE_VALUE_MAP.get(value)
    if mapped_value is not None:
        return mapped_value

    return _parse_float(value, field_name=field_name)


def _parse_float(value: str | None, *, field_name: str) -> float:
    if value is None:
        raise ValueError(f"Missing required numeric field `{field_name}`")

    try:
        return float(value)
    except ValueError as error:
        raise ValueError(f"Invalid numeric value for `{field_name}`: {value}") from error
