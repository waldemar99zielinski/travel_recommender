from __future__ import annotations

import csv
from pathlib import Path

from embeddings.protocols import TextEmbeddingModelProtocol


class FakeTextEmbeddingModel(TextEmbeddingModelProtocol):
    """Deterministic embedding model for storage bootstrap tests."""

    def __init__(self, dimensions: int = 8) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions must be greater than zero")
        self._dimensions = dimensions

    def check_health(self) -> bool:
        return True

    def get_dimentions(self) -> int:
        return self._dimensions

    def embed_query(self, text: str) -> list[float]:
        normalized = text.strip()
        if not normalized:
            raise ValueError("text must not be empty")

        base_value = float(sum(ord(character) for character in normalized) % 1000) / 1000.0
        return [base_value + (index * 0.001) for index in range(self._dimensions)]


def count_seed_rows(csv_file_path: Path) -> int:
    """Count source CSV rows that represent destinations."""
    with csv_file_path.open(mode="r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=";")
        return sum(1 for row in reader if (row.get("u_name") or "").strip())


def load_seed_destination_ids(csv_file_path: Path) -> set[str]:
    """Load unique destination IDs from CSV rows with `u_name` populated."""
    with csv_file_path.open(mode="r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=";")
        destination_ids = {(row.get("u_name") or "").strip() for row in reader}
        destination_ids.discard("")
        return destination_ids
