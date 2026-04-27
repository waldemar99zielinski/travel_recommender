from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[4]))

from storage.bootstrap_travel_destinations import bootstrap_travel_destinations_from_csv
from storage.bootstrap.travel_destination_csv_bootstrap import load_travel_destination_records_from_csv
from storage.configuration import MigrationConfiguration
from storage.configuration import StorageConfiguration
from storage.configuration import StorageEngineConfiguration
from storage.test.utils import FakeTextEmbeddingModel
from storage.test.utils import build_db_url_with_schema_search_path
from storage.test.utils import count_persisted_destinations
from storage.test.utils import create_schema
from storage.test.utils import drop_schema
from storage.test.utils import generate_schema_name
from storage.test.utils import load_persisted_destination_ids

DEVELOPMENT_BASE_DB_URL = (
    "postgresql+psycopg://"
    "hybrid_dev:change_me_dev_password@localhost:5432/recommender"
)

REAL_DATA_DIR = Path(__file__).resolve().parents[5] / "data"
E2E_DATA_DIR = Path(__file__).resolve().parents[1] / "data"

DETAILED_CSV_PATH = REAL_DATA_DIR / "regionmodel_with_detailed_descriptions.csv"
DESCRIPTION_CSV_PATH = REAL_DATA_DIR / "regionmodel_description.csv"
PARTIAL_INVALID_CSV_PATH = E2E_DATA_DIR / "travel_destinations_partial_invalid.csv"
QUERY_MATCHING_CSV_PATH = E2E_DATA_DIR / "travel_destinations_query_matching.csv"


class TestBootstrapTravelDestinationsDataSourcesE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        required_csv_paths = (
            DETAILED_CSV_PATH,
            DESCRIPTION_CSV_PATH,
            PARTIAL_INVALID_CSV_PATH,
            QUERY_MATCHING_CSV_PATH,
        )
        missing_paths = [path for path in required_csv_paths if not path.exists()]
        if missing_paths:
            missing_paths_text = ", ".join(str(path) for path in missing_paths)
            raise unittest.SkipTest(f"CSV seed file not found: {missing_paths_text}")

        cls.base_db_url = DEVELOPMENT_BASE_DB_URL
        cls.embedding_model = FakeTextEmbeddingModel(dimensions=8)

    def setUp(self) -> None:
        self.schema_name = generate_schema_name(prefix="test_storage_bootstrap_sources")
        create_schema(self.base_db_url, self.schema_name)
        self.schema_db_url = build_db_url_with_schema_search_path(self.base_db_url, self.schema_name)
        self.storage_configuration = StorageConfiguration(
            engine=StorageEngineConfiguration(db_url=self.schema_db_url),
            migrations=MigrationConfiguration(enabled=True),
            schema_name=self.schema_name,
        )

    def tearDown(self) -> None:
        drop_schema(self.base_db_url, self.schema_name)

    def test_bootstrap_supports_backend_detailed_csv(self) -> None:
        expected_records = load_travel_destination_records_from_csv(
            DETAILED_CSV_PATH,
            embedding_model=self.embedding_model,
        )
        expected_row_count = len(expected_records)
        expected_destination_ids = {record.id for record in expected_records}

        inserted_rows = self._bootstrap(DETAILED_CSV_PATH)

        self.assertEqual(inserted_rows, expected_row_count)
        self.assertEqual(count_persisted_destinations(self.schema_db_url), expected_row_count)
        self.assertSetEqual(load_persisted_destination_ids(self.schema_db_url), expected_destination_ids)

    def test_bootstrap_supports_backend_description_csv(self) -> None:
        expected_records = load_travel_destination_records_from_csv(
            DESCRIPTION_CSV_PATH,
            embedding_model=self.embedding_model,
        )
        expected_row_count = len(expected_records)
        expected_destination_ids = {record.id for record in expected_records}

        inserted_rows = self._bootstrap(DESCRIPTION_CSV_PATH)

        self.assertEqual(inserted_rows, expected_row_count)
        self.assertEqual(count_persisted_destinations(self.schema_db_url), expected_row_count)
        self.assertSetEqual(load_persisted_destination_ids(self.schema_db_url), expected_destination_ids)

    def test_bootstrap_skips_invalid_rows_in_partial_invalid_fixture(self) -> None:
        inserted_rows = self._bootstrap(PARTIAL_INVALID_CSV_PATH)

        expected_destination_ids = {"VAL_BEACH", "VAL_SKI"}
        self.assertEqual(inserted_rows, len(expected_destination_ids))
        self.assertSetEqual(load_persisted_destination_ids(self.schema_db_url), expected_destination_ids)

    def test_bootstrap_supports_query_matching_fixture(self) -> None:
        expected_records = load_travel_destination_records_from_csv(
            QUERY_MATCHING_CSV_PATH,
            embedding_model=self.embedding_model,
        )
        expected_row_count = len(expected_records)
        expected_destination_ids = {record.id for record in expected_records}

        inserted_rows = self._bootstrap(QUERY_MATCHING_CSV_PATH)

        self.assertEqual(inserted_rows, expected_row_count)
        self.assertSetEqual(load_persisted_destination_ids(self.schema_db_url), expected_destination_ids)

    def _bootstrap(self, csv_file_path: Path) -> int:
        return bootstrap_travel_destinations_from_csv(
            csv_file_path=csv_file_path,
            storage_configuration=self.storage_configuration,
            embedding_model=self.embedding_model,
            batch_size=64,
        )


if __name__ == "__main__":
    unittest.main()
