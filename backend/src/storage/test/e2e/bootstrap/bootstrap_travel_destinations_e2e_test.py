from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[4]))

from storage.bootstrap_travel_destinations import bootstrap_travel_destinations_from_csv
from storage.configuration import MigrationConfiguration
from storage.configuration import StorageConfiguration
from storage.configuration import StorageEngineConfiguration
from storage.test.utils import FakeTextEmbeddingModel
from storage.test.utils import build_db_url_with_schema_search_path
from storage.test.utils import count_persisted_destinations
from storage.test.utils import count_seed_rows
from storage.test.utils import create_schema
from storage.test.utils import drop_schema
from storage.test.utils import generate_schema_name
from storage.test.utils import load_persisted_destination_ids
from storage.test.utils import load_seed_destination_ids

SEED_CSV_PATH = Path(__file__).resolve().parents[5] / "data" / "regionmodel_with_detailed_descriptions.csv"
DEVELOPMENT_BASE_DB_URL = (
    "postgresql+psycopg://"
    "hybrid_dev:change_me_dev_password@localhost:5432/recommender"
)


class TestBootstrapTravelDestinationsE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not SEED_CSV_PATH.exists():
            raise unittest.SkipTest(f"CSV seed file not found: {SEED_CSV_PATH}")

        cls.base_db_url = DEVELOPMENT_BASE_DB_URL
        cls.embedding_model = FakeTextEmbeddingModel(dimensions=8)
        cls.expected_row_count = count_seed_rows(SEED_CSV_PATH)
        cls.expected_destination_ids = load_seed_destination_ids(SEED_CSV_PATH)

    def setUp(self) -> None:
        self.schema_name = generate_schema_name()
        create_schema(self.base_db_url, self.schema_name)
        schema_db_url = build_db_url_with_schema_search_path(self.base_db_url, self.schema_name)
        self.storage_configuration = StorageConfiguration(
            engine=StorageEngineConfiguration(db_url=schema_db_url),
            migrations=MigrationConfiguration(enabled=True),
            schema_name=self.schema_name,
        )
        self.schema_db_url = schema_db_url

    def tearDown(self) -> None:
        drop_schema(self.base_db_url, self.schema_name)

    def test_bootstrap_inserts_expected_number_of_destinations(self) -> None:
        inserted_rows = bootstrap_travel_destinations_from_csv(
            csv_file_path=SEED_CSV_PATH,
            storage_configuration=self.storage_configuration,
            embedding_model=self.embedding_model,
            batch_size=64,
        )

        self.assertEqual(inserted_rows, self.expected_row_count)
        self.assertEqual(count_persisted_destinations(self.schema_db_url), self.expected_row_count)

    def test_bootstrap_is_idempotent_for_same_csv(self) -> None:
        first_inserted_rows = bootstrap_travel_destinations_from_csv(
            csv_file_path=SEED_CSV_PATH,
            storage_configuration=self.storage_configuration,
            embedding_model=self.embedding_model,
            batch_size=64,
        )
        second_inserted_rows = bootstrap_travel_destinations_from_csv(
            csv_file_path=SEED_CSV_PATH,
            storage_configuration=self.storage_configuration,
            embedding_model=self.embedding_model,
            batch_size=64,
        )

        self.assertEqual(first_inserted_rows, self.expected_row_count)
        self.assertEqual(second_inserted_rows, self.expected_row_count)
        self.assertEqual(count_persisted_destinations(self.schema_db_url), self.expected_row_count)

    def test_bootstrap_persists_all_destination_ids_from_csv(self) -> None:
        bootstrap_travel_destinations_from_csv(
            csv_file_path=SEED_CSV_PATH,
            storage_configuration=self.storage_configuration,
            embedding_model=self.embedding_model,
            batch_size=64,
        )

        persisted_destination_ids = load_persisted_destination_ids(self.schema_db_url)
        self.assertSetEqual(persisted_destination_ids, self.expected_destination_ids)


if __name__ == "__main__":
    unittest.main()
