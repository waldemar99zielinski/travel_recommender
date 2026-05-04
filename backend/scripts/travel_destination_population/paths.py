from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = BACKEND_ROOT / "src"
DATA_DIRECTORY = BACKEND_ROOT / "data"

DEFAULT_GENERATED_CSV_PATH = DATA_DIRECTORY / "regionmodel_with_generated_descriptions.csv"
DEFAULT_DETAILED_CSV_PATH = DATA_DIRECTORY / "regionmodel_with_detailed_descriptions.csv"


def ensure_src_path() -> None:
    """Ensure backend src modules are importable when the script runs directly."""
    if str(SRC_PATH) not in sys.path:
        sys.path.insert(0, str(SRC_PATH))


def resolve_default_csv_path() -> Path:
    """Prefer generated descriptions when present, otherwise fall back to the seed CSV."""
    if DEFAULT_GENERATED_CSV_PATH.exists():
        return DEFAULT_GENERATED_CSV_PATH
    return DEFAULT_DETAILED_CSV_PATH
