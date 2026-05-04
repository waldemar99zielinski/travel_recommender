from __future__ import annotations

import csv
from pathlib import Path

from region_description_generation.context import RegionCatalogAnalysis
from region_description_generation.context import is_placeholder_description
from region_description_generation.agent import RegionDescriptionGenerationAgent

from region_description_generation.paths import ensure_src_path

ensure_src_path()

from storage.models.travel_destination import TravelDestinationRecord


def load_csv_rows(csv_path: Path) -> tuple[list[dict[str, str]], list[str]]:
    """Load the seed CSV that will receive updated descriptions."""
    with csv_path.open(mode="r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=";")
        if reader.fieldnames is None:
            raise ValueError(f"CSV file has no header: {csv_path}")
        return list(reader), list(reader.fieldnames)


def write_csv_rows(
    output_csv_path: Path,
    *,
    rows: list[dict[str, str]],
    fieldnames: list[str],
) -> None:
    """Write the updated destination CSV with semicolon delimiters."""
    with output_csv_path.open(mode="w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def update_rows_with_generated_descriptions(
    *,
    rows: list[dict[str, str]],
    target_records: list[TravelDestinationRecord],
    analysis: RegionCatalogAnalysis,
    agent: RegionDescriptionGenerationAgent,
    only_placeholder: bool,
) -> int:
    """Generate fresh descriptions and update matching CSV rows in memory."""
    rows_by_id = {
        (row.get("u_name") or "").strip(): row
        for row in rows
        if (row.get("u_name") or "").strip()
    }
    catalog_summary = analysis.to_prompt_summary()
    updated_count = 0

    for index, record in enumerate(target_records, start=1):
        row = rows_by_id.get(record.id)
        if row is None:
            print(f"[{index}/{len(target_records)}] skipping {record.id}: missing CSV row")
            continue

        if only_placeholder and not is_placeholder_description(row.get("description")):
            print(f"[{index}/{len(target_records)}] skipping {record.id}: description already looks specific")
            continue

        print(f"[{index}/{len(target_records)}] researching {record.id} ({record.region})")
        description = agent.generate_description(
            context=analysis.build_region_context(record),
            catalog_summary=catalog_summary,
        )
        row["description"] = description
        updated_count += 1

    return updated_count
