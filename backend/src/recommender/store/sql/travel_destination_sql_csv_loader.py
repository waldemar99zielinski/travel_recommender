from __future__ import annotations

from recommender.models.data_flow.travel_destination import TravelDestination as TravelDestinationModel
from recommender.store.sql.travel_destination_table import TravelDestinationTable
from recommender.store.utils.travel_destination_csv_data_loader import (
    TravelDestinationCsvDataLoader,
)


class TravelDestinationSqlCsvLoader:
    """Converts validated travel destination CSV rows into SQL table models."""

    def __init__(self, data_loader: TravelDestinationCsvDataLoader | None = None) -> None:
        self.data_loader = data_loader or TravelDestinationCsvDataLoader()

    def load(self, csv_file_path: str) -> list[TravelDestinationTable]:
        travel_destinations = self.data_loader.load(csv_file_path)
        models: list[TravelDestinationTable] = []

        for travel_destination in travel_destinations:
            models.append(
                self._travel_destination_to_table_model(
                    travel_destination=travel_destination,
                    csv_file_path=csv_file_path,
                )
            )

        return models

    def _travel_destination_to_table_model(
        self,
        travel_destination: TravelDestinationModel,
        csv_file_path: str,
    ) -> TravelDestinationTable:
        payload = travel_destination.model_dump()
        payload["id"] = payload.pop("u_name")

        try:
            return TravelDestinationTable(**payload)
        except Exception as error:
            row_info = {
                "csv_file": csv_file_path,
                "region": travel_destination.region,
                "u_name": travel_destination.u_name,
            }
            raise ValueError(f"Invalid CSV row for TravelDestinationTable {row_info}: {error}") from error
