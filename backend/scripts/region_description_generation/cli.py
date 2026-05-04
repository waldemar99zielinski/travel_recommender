from __future__ import annotations

import argparse
from pathlib import Path

from region_description_generation.agent import RegionDescriptionGenerationAgent
from region_description_generation.catalog import load_regions_from_store
from region_description_generation.catalog import select_target_records
from region_description_generation.context import analyze_region_catalog
from region_description_generation.csv_io import load_csv_rows
from region_description_generation.csv_io import update_rows_with_generated_descriptions
from region_description_generation.csv_io import write_csv_rows
from region_description_generation.paths import DEFAULT_INPUT_CSV_PATH
from region_description_generation.paths import DEFAULT_OUTPUT_CSV_PATH


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the description generation script."""
    parser = argparse.ArgumentParser(
        description="Generate detailed region descriptions through TravelDestinationStore + OpenAI web search.",
    )
    parser.add_argument(
        "--input-csv",
        type=Path,
        default=DEFAULT_INPUT_CSV_PATH,
        help="CSV file to read and update.",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=DEFAULT_OUTPUT_CSV_PATH,
        help="CSV file to write with generated descriptions.",
    )
    parser.add_argument(
        "--region-id",
        action="append",
        default=[],
        help="Optional region id to regenerate. Repeat the flag for multiple ids.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional cap on number of persisted regions to process after filtering.",
    )
    parser.add_argument(
        "--only-placeholder",
        action="store_true",
        help="Only regenerate blank or clearly generic descriptions.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-5.4",
        help="OpenAI model name used for the research agent.",
    )
    parser.add_argument(
        "--search-tool",
        type=str,
        choices=("web_search_preview", "web_search"),
        default="web_search_preview",
        help="Built-in OpenAI web search tool type.",
    )
    parser.add_argument(
        "--search-context-size",
        type=str,
        choices=("low", "medium", "high"),
        default="high",
        help="How much search context to retrieve for each region.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.2,
        help="Model temperature for generation.",
    )
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=900,
        help="Maximum output tokens per generated description.",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    """Validate CLI argument values before processing starts."""
    if args.limit is not None and args.limit <= 0:
        raise ValueError("--limit must be greater than zero")
    if args.max_output_tokens <= 0:
        raise ValueError("--max-output-tokens must be greater than zero")
    if not args.input_csv.exists():
        raise FileNotFoundError(f"Input CSV does not exist: {args.input_csv}")


def main() -> None:
    """Run the region description generation workflow end to end."""
    args = parse_args()
    validate_args(args)

    records = load_regions_from_store()
    analysis = analyze_region_catalog(records)
    target_records = select_target_records(
        records,
        region_ids=args.region_id,
        limit=args.limit,
    )

    rows, fieldnames = load_csv_rows(args.input_csv)
    agent = RegionDescriptionGenerationAgent(
        model=args.model,
        search_tool=args.search_tool,
        search_context_size=args.search_context_size,
        temperature=args.temperature,
        max_output_tokens=args.max_output_tokens,
    )

    print(analysis.to_prompt_summary())
    print(f"Selected {len(target_records)} region(s) for regeneration")

    updated_count = update_rows_with_generated_descriptions(
        rows=rows,
        target_records=target_records,
        analysis=analysis,
        agent=agent,
        only_placeholder=args.only_placeholder,
    )

    write_csv_rows(
        args.output_csv,
        rows=rows,
        fieldnames=fieldnames,
    )

    print(f"Updated {updated_count} region description(s)")
    print(f"Wrote output CSV to {args.output_csv}")
