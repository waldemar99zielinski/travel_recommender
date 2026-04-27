from storage.bootstrap.travel_destination_csv_bootstrap import (
    load_travel_destination_records_from_csv,
)
from storage.bootstrap.travel_destination_seed import seed_travel_destinations

__all__ = [
    "load_travel_destination_records_from_csv",
    "seed_travel_destinations",
]
