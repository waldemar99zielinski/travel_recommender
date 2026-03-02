import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from recommender.common.configuration import VectorStoreConfiguration
from recommender.store.vector.travel_destination_vector_store import (
    TravelDestinationVectorStore,
)

class TestTravelDestinationVectorStore(unittest.TestCase):
    def setUp(self) -> None:
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.valid_csv = self.test_data_dir / "travel_destinations_vector_valid.csv"
        self.temp_dir = TemporaryDirectory()
        self.db_path = str(Path(self.temp_dir.name) / "vector_index")
        self.store_config = VectorStoreConfiguration(db_path=self.db_path)

        self.store = TravelDestinationVectorStore(store_config=self.store_config)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_build_from_csv_creates_index_and_size(self) -> None:
        self.store.build_from_csv(str(self.valid_csv))

        self.assertTrue(self.store.is_loaded())
        self.assertEqual(self.store.size(), 3)

    def test_search_returns_expected_semantic_match(self) -> None:
        self.store.build_from_csv(str(self.valid_csv))

        food_results = self.store.search("sushi food city", k=1)
        self.assertEqual(len(food_results), 1)
        self.assertEqual(food_results[0].u_name, "JPN")

        beach_results = self.store.search("beach ocean sunshine", k=1)
        self.assertEqual(len(beach_results), 1)
        self.assertEqual(beach_results[0].u_name, "PRT")

    def test_load_from_disk_and_search_all_ranked(self) -> None:
        self.store.build_from_csv(str(self.valid_csv))

        reloaded_store = TravelDestinationVectorStore(store_config=self.store_config)

        results = reloaded_store.search_all_ranked("mountain hiking")
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].u_name, "NOR")


if __name__ == "__main__":
    unittest.main()
