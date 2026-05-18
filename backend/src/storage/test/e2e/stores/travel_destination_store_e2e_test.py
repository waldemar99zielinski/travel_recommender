from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[4]))

from storage.bootstrap_travel_destinations import bootstrap_travel_destinations_from_csv
from storage.configuration import MigrationConfiguration
from storage.configuration import StorageConfiguration
from storage.configuration import StorageEngineConfiguration
from storage.storage import Storage
from storage.stores.search_models import TravelSearchConstraints
from storage.test.utils import KeywordTextEmbeddingModel
from storage.test.utils import build_db_url_with_schema_search_path
from storage.test.utils import create_schema
from storage.test.utils import drop_schema
from storage.test.utils import generate_schema_name

DEVELOPMENT_BASE_DB_URL = (
    "postgresql+psycopg://"
    "hybrid_dev:change_me_dev_password@localhost:5432/recommender"
)

QUERY_MATCHING_CSV_PATH = Path(__file__).resolve().parents[1] / "data" / "travel_destinations_query_matching.csv"


class TestTravelDestinationStoreE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not QUERY_MATCHING_CSV_PATH.exists():
            raise unittest.SkipTest(f"CSV seed file not found: {QUERY_MATCHING_CSV_PATH}")

        cls.base_db_url = DEVELOPMENT_BASE_DB_URL
        cls.embedding_model = KeywordTextEmbeddingModel()

    def setUp(self) -> None:
        self.schema_name = generate_schema_name(prefix="test_storage_travel_store")
        create_schema(self.base_db_url, self.schema_name)
        schema_db_url = build_db_url_with_schema_search_path(self.base_db_url, self.schema_name)
        self.storage_configuration = StorageConfiguration(
            engine=StorageEngineConfiguration(db_url=schema_db_url),
            migrations=MigrationConfiguration(enabled=True),
            schema_name=self.schema_name,
        )

        bootstrap_travel_destinations_from_csv(
            csv_file_path=QUERY_MATCHING_CSV_PATH,
            storage_configuration=self.storage_configuration,
            embedding_model=self.embedding_model,
            batch_size=32,
        )

    def tearDown(self) -> None:
        drop_schema(self.base_db_url, self.schema_name)

    def test_semantic_search_returns_expected_top_destination(self) -> None:
        with Storage(self.storage_configuration, embedding_model=self.embedding_model) as storage:
            results = storage.travel_destinations.semantic_search("alpine ski snow mountain", limit=3)

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].destination.id, "ALP_SKI")

    def test_hybrid_search_uses_cost_constraint_for_ranking(self) -> None:
        constraints = TravelSearchConstraints(max_cost_per_week=800.0)

        with Storage(self.storage_configuration, embedding_model=self.embedding_model) as storage:
            semantic_only_results = storage.travel_destinations.hybrid_search(
                "luxury tropical beach resort",
                constraints=TravelSearchConstraints(),
                limit=5,
                semantic_weight=1.0,
                logistics_weight=0.0,
            )
            constrained_results = storage.travel_destinations.hybrid_search(
                "luxury tropical beach resort",
                constraints=constraints,
                limit=5,
                semantic_weight=0.2,
                logistics_weight=0.8,
            )

        semantic_ids = [result.destination.id for result in semantic_only_results]
        constrained_ids = [result.destination.id for result in constrained_results]

        self.assertEqual(semantic_ids[0], "LUX_BEACH")
        self.assertIn("ISL_BEACH", constrained_ids)
        self.assertIn("LUX_BEACH", constrained_ids)
        self.assertLess(constrained_ids.index("ISL_BEACH"), constrained_ids.index("LUX_BEACH"))

    def test_vector_search_matches_semantic_search_alias(self) -> None:
        with Storage(self.storage_configuration, embedding_model=self.embedding_model) as storage:
            semantic_results = storage.travel_destinations.semantic_search(
                "museum culture architecture",
                limit=2,
            )
            vector_results = storage.travel_destinations.vector_search(
                "museum culture architecture",
                limit=2,
            )

        semantic_ids = [result.destination.id for result in semantic_results]
        vector_ids = [result.destination.id for result in vector_results]

        self.assertEqual(semantic_ids, vector_ids)
        self.assertEqual(semantic_ids[0], "CITY_CULT")

    def test_exact_text_search_matches_region_name(self) -> None:
        with Storage(self.storage_configuration, embedding_model=self.embedding_model) as storage:
            results = storage.travel_destinations.exact_text_search("Culture Capital", limit=3)

        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0].destination.id, "CITY_CULT")

    def test_exact_text_search_matches_description_terms(self) -> None:
        with Storage(self.storage_configuration, embedding_model=self.embedding_model) as storage:
            results = storage.travel_destinations.exact_text_search("exclusive sea views", limit=3)

        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0].destination.id, "LUX_BEACH")

    def test_semantic_search_can_filter_destination_ids(self) -> None:
        with Storage(self.storage_configuration, embedding_model=self.embedding_model) as storage:
            results = storage.travel_destinations.semantic_search(
                "museum culture architecture",
                limit=3,
                destination_ids=["CITY_CULT"],
            )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].destination.id, "CITY_CULT")

    def test_semantic_search_rejects_blank_query(self) -> None:
        with Storage(self.storage_configuration, embedding_model=self.embedding_model) as storage:
            with self.assertRaises(ValueError):
                storage.travel_destinations.semantic_search("   ")


if __name__ == "__main__":
    unittest.main()
