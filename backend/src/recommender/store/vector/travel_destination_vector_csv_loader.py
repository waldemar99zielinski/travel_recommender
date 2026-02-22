from __future__ import annotations

from langchain_core.documents import Document

from recommender.store.utils.travel_destination_csv_data_loader import (
    TravelDestinationCsvDataLoader,
)
from recommender.store.vector.travel_destination_document_mapper import (
    TravelDestinationDocumentMapper,
)


class TravelDestinationVectorCsvLoader:
    """Loads travel destinations from CSV and maps them to FAISS-compatible Documents."""

    def __init__(
        self,
        csv_data_loader: TravelDestinationCsvDataLoader | None = None,
        document_mapper: TravelDestinationDocumentMapper | None = None,
    ) -> None:
        self.csv_data_loader = csv_data_loader or TravelDestinationCsvDataLoader()
        self.document_mapper = document_mapper or TravelDestinationDocumentMapper()

    def load(self, csv_file_path: str) -> list[Document]:
        destinations = self.csv_data_loader.load(csv_file_path)
        return [
            self.document_mapper.to_document(destination=destination, source=csv_file_path)
            for destination in destinations
        ]
