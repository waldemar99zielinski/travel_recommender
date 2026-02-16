import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from sqlalchemy import func
from sqlmodel import select

from recommender.store.sql.travel_destination_store import SqlStore
from recommender.store.sql.travel_destination_table import TravelDestinationTable


class TestSqlStoreCsvLoading(unittest.TestCase):
    def setUp(self) -> None:
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.temp_dir = TemporaryDirectory()
        db_file = Path(self.temp_dir.name) / "travel_destinations.db"
        self.store = SqlStore(f"sqlite:///{db_file}")
        self.store.load()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_load_valid_csv_skips_rows_without_identifier(self) -> None:
        valid_csv = self.test_data_dir / "travel_destinations_valid.csv"

        self.store.load_travel_destinations_data_from_csv(str(valid_csv), mode="replace")

        self.assertEqual(self.store.size(TravelDestinationTable), 4)
        rows = self.store.all(TravelDestinationTable)
        self.assertEqual({row.id for row in rows}, {"PRT", "JPN", "NOR", "THA"})

    def test_load_invalid_preference_row_raises_error(self) -> None:
        invalid_csv = self.test_data_dir / "travel_destinations_invalid_preference.csv"

        with self.assertRaises(ValueError):
            self.store.load_travel_destinations_data_from_csv(str(invalid_csv), mode="replace")

        self.assertEqual(self.store.size(TravelDestinationTable), 0)

    def test_load_missing_required_field_raises_error(self) -> None:
        missing_required_csv = self.test_data_dir / "travel_destinations_missing_required.csv"

        with self.assertRaises(ValueError):
            self.store.load_travel_destinations_data_from_csv(str(missing_required_csv), mode="replace")

        self.assertEqual(self.store.size(TravelDestinationTable), 0)


class TestSqlStoreQuerying(unittest.TestCase):
    def setUp(self) -> None:
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.temp_dir = TemporaryDirectory()
        db_file = Path(self.temp_dir.name) / "travel_destinations.db"
        self.store = SqlStore(f"sqlite:///{db_file}")
        self.store.load()

        valid_csv = self.test_data_dir / "travel_destinations_valid.csv"
        self.store.load_travel_destinations_data_from_csv(str(valid_csv), mode="replace")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_query_subset_by_region(self) -> None:
        statement = select(TravelDestinationTable).where(TravelDestinationTable.region == "Portugal")

        result = self.store.query(statement)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, "PRT")

    def test_query_subset_by_numeric_threshold(self) -> None:
        statement = select(TravelDestinationTable).where(TravelDestinationTable.cost_per_week > 1000)

        result = self.store.query(statement)

        self.assertEqual(len(result), 2)
        self.assertEqual({row.id for row in result}, {"JPN", "NOR"})

    def test_query_subset_by_normalized_preference(self) -> None:
        statement = select(TravelDestinationTable).where(TravelDestinationTable.popularity >= 0.75)

        result = self.store.query(statement)

        self.assertEqual(len(result), 3)
        self.assertEqual({row.id for row in result}, {"PRT", "JPN", "THA"})

    def test_query_subset_by_parent_region(self) -> None:
        statement = select(TravelDestinationTable).where(TravelDestinationTable.parent_region == "Europe")

        result = self.store.query(statement)

        self.assertEqual(len(result), 2)
        self.assertEqual({row.id for row in result}, {"PRT", "NOR"})

    def test_query_subset_by_description_contains(self) -> None:
        statement = select(TravelDestinationTable).where(
            func.lower(TravelDestinationTable.description).like("%food%")
        )

        result = self.store.query(statement)

        self.assertEqual(len(result), 2)
        self.assertEqual({row.id for row in result}, {"JPN", "THA"})

    def test_query_subset_by_combined_conditions(self) -> None:
        statement = select(TravelDestinationTable).where(
            TravelDestinationTable.popularity >= 0.75,
            TravelDestinationTable.cost_per_week < 1000,
        )

        result = self.store.query(statement)

        self.assertEqual(len(result), 2)
        self.assertEqual({row.id for row in result}, {"PRT", "THA"})

    def test_append_and_replace_modes(self) -> None:
        additional_csv = self.test_data_dir / "travel_destinations_additional.csv"

        self.store.load_travel_destinations_data_from_csv(str(additional_csv), mode="append")
        self.assertEqual(self.store.size(TravelDestinationTable), 5)

        self.store.load_travel_destinations_data_from_csv(str(additional_csv), mode="replace")
        self.assertEqual(self.store.size(TravelDestinationTable), 1)


    def test_all_returns_all_rows(self) -> None:
        rows = self.store.all(TravelDestinationTable)

        self.assertEqual(len(rows), 4)


if __name__ == "__main__":
    unittest.main()
