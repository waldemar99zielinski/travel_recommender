from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from recommender.models.data_flow.travel_destination import TravelDestination as TravelDestinationModel
from pydantic import ValidationError
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


class TravelDestinationCsvDataLoader:
    """Loads and validates travel destination CSV rows into TravelDestination models."""

    def load(self, csv_file_path: str) -> list[TravelDestinationModel]:
        csv_file = Path(csv_file_path)
        if not csv_file.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_file}")

        validated_rows: list[TravelDestinationModel] = []
        with csv_file.open(mode="r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file, delimiter=";")
            for row_index, row in enumerate(reader):
                if not self._has_row_identifier(row):
                    logger.debug(
                        "Skipping CSV row without identifier `u_name`: row_index=%s, csv_file=%s",
                        row_index + 1,
                        csv_file,
                    )
                    continue

                validated_rows.append(self._row_to_travel_destination_model(row, row_index, csv_file))

        return validated_rows

    def _row_to_travel_destination_model(
        self,
        row: dict[str, str],
        row_index: int,
        csv_file: Path,
    ) -> TravelDestinationModel:
        normalized_row = self._normalize_row(row)
        payload: dict[str, Any] = {
            "parent_region": normalized_row.get("parent_region"),
            "region": normalized_row.get("region"),
            "u_name": normalized_row.get("u_name"),
            "cost_per_week": normalized_row.get("cost_per_week"),
            "description": normalized_row.get("description"),
        }

        for field_name in PREFERENCE_FIELDS:
            payload[field_name] = self._to_preference_input(normalized_row.get(field_name))

        try:
            return TravelDestinationModel(**payload)
        except ValidationError as error:
            csv_row_number = row_index + 1
            field_errors = []
            for validation_error in error.errors():
                location = validation_error.get("loc", ())
                field_name = str(location[0]) if location else "unknown"
                message = validation_error.get("msg", "validation error")
                field_errors.append(f"{field_name}: {message}")

            details = "; ".join(field_errors)
            raise ValueError(
                "Invalid TravelDestination model values in CSV row "
                f"{csv_row_number} ({csv_file}): {details}"
            ) from error

    def _normalize_row(self, row: dict[str, str]) -> dict[str, Any]:
        normalized_row: dict[str, Any] = {}
        for key, value in row.items():
            normalized = self._normalize_optional_text(value)
            if normalized is not None:
                normalized_row[key] = normalized
        return normalized_row

    def _to_preference_input(self, value: str | None) -> float | str | None:
        if value is None:
            return None

        mapped = PREFERENCE_VALUE_MAP.get(value)
        if mapped is not None:
            return mapped

        try:
            numeric = float(value)
            return numeric
        except ValueError:
            logger.warning("Preference value '%s' not present in mapping", value)
            return value

    def _normalize_optional_text(self, value: Any) -> str | None:
        if value is None:
            return None

        normalized = str(value).strip()
        return normalized if normalized else None

    def _has_row_identifier(self, row: dict[str, str]) -> bool:
        return self._normalize_optional_text(row.get("u_name")) is not None
