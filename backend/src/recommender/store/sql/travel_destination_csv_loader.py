from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from recommender.store.sql.travel_destination_table import TravelDestinationTable
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

PREFERENCE_VALUE_MAP: dict[str, float] = {
    "--": 0.0,
    "-": 0.25,
    "o": 0.5,
    "+": 0.75,
    "++": 1.0,
}

PREFERENCE_FIELDS: tuple[str, ...] = (
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
    "safety",
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

REQUIRED_SOURCE_FIELDS: tuple[str, ...] = (
    "u_name",
    "Parent_region",
    "Region",
    "costPerWeek",
    "Description",
) + PREFERENCE_FIELDS


class TravelDestinationCsvLoader:
    """Loads and converts CSV rows into TravelDestinationTable models."""

    def load(self, csv_file_path: str) -> list[TravelDestinationTable]:
        csv_file = Path(csv_file_path)
        if not csv_file.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_file}")

        rows: list[TravelDestinationTable] = []
        with csv_file.open(mode="r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file, delimiter=";")
            for row_index, row in enumerate(reader):
                if not self._has_row_identifier(row):
                    logger.debug(
                        "Skipping CSV row without identifier `u_name`: row_index=%s, csv_file=%s",
                        row_index,
                        csv_file,
                    )
                    continue

                if not self._is_complete_row(row):
                    raise ValueError(
                        "CSV row contains missing required fields: "
                        f"row_index={row_index}, csv_file={csv_file}, u_name={row.get('u_name')!r}"
                    )

                rows.append(self._row_to_model(row=row, row_index=row_index, csv_file=csv_file))

        return rows

    def _row_to_model(
        self,
        row: dict[str, str],
        row_index: int,
        csv_file: Path,
    ) -> TravelDestinationTable:
        payload: dict[str, Any] = {
            "id": self._normalize_text(row.get("u_name")),
            "parent_region": self._normalize_text(row.get("Parent_region")),
            "region": self._normalize_text(row.get("Region")),
            "cost_per_week": self._to_float(row.get("costPerWeek")),
            "description": self._normalize_text(row.get("Description")),
        }

        for field_name in PREFERENCE_FIELDS:
            payload[field_name] = self._to_preference_value(row.get(field_name))

        try:
            return TravelDestinationTable(**payload)
        except Exception as error:
            row_info = {
                "row_index": row_index,
                "csv_file": str(csv_file),
                "region": row.get("Region"),
                "u_name": row.get("u_name"),
            }
            raise ValueError(f"Invalid CSV row for TravelDestinationTable {row_info}: {error}") from error

    def _to_preference_value(self, value: Any) -> float:
        normalized = self._normalize_text(value)
        if normalized is None:
            raise ValueError("Missing preference value")

        mapped = PREFERENCE_VALUE_MAP.get(normalized)
        if mapped is None:
            raise ValueError(f"Unsupported preference value: {normalized}")

        return mapped

    def _to_float(self, value: Any) -> float:
        normalized = self._normalize_text(value)
        if normalized is None:
            raise ValueError("Missing numeric value")

        return float(normalized)

    def _normalize_text(self, value: Any) -> str:
        if value is None:
            raise ValueError("Missing text value")

        normalized = str(value).strip()
        if not normalized:
            raise ValueError("Empty text value")

        return normalized

    def _normalize_optional_text(self, value: Any) -> str | None:
        if value is None:
            return None

        normalized = str(value).strip()
        return normalized if normalized else None

    def _has_row_identifier(self, row: dict[str, str]) -> bool:
        return self._normalize_optional_text(row.get("u_name")) is not None

    def _is_complete_row(self, row: dict[str, str]) -> bool:
        for field_name in REQUIRED_SOURCE_FIELDS:
            if self._normalize_optional_text(row.get(field_name)) is None:
                return False
        return True
