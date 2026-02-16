import unittest

from pydantic import ValidationError

from recommender.store.models.travel_destination import PREFERENCE_FIELDS
from recommender.store.models.travel_destination import TravelDestination


class TestTravelDestination(unittest.TestCase):
    def _base_destination_payload(self) -> dict:
        return {
            "parent_region": "Europe",
            "region": "Portugal",
            "u_name": "PRT",
            "popularity": "+",
            "cost_per_week": 900.0,
            "jan": "--",
            "feb": "-",
            "mar": "o",
            "apr": "+",
            "may": "++",
            "jun": "o",
            "jul": "+",
            "aug": "+",
            "sep": "o",
            "oct": "-",
            "nov": "--",
            "dec": "o",
            "safety": "++",
            "nature": "+",
            "hiking": "o",
            "beach": "++",
            "watersports": "+",
            "entertainment": "o",
            "wintersports": "--",
            "culture": "+",
            "culinary": "++",
            "architecture": "o",
            "shopping": "-",
            "description": "A warm destination with rich culture and coast.",
        }

    def test_creation_converts_symbol_preferences_to_numeric_scores(self):
        base_payload = self._base_destination_payload()
        destination = TravelDestination(**base_payload)

        self.assertEqual(destination.popularity, 0.75)
        self.assertEqual(destination.jan, 0.0)
        self.assertEqual(destination.feb, 0.25)
        self.assertEqual(destination.mar, 0.5)
        self.assertEqual(destination.apr, 0.75)
        self.assertEqual(destination.may, 1.0)
        self.assertEqual(destination.safety, 1.0)
        self.assertEqual(destination.shopping, 0.25)

        self.assertEqual(destination.parent_region, base_payload["parent_region"])
        self.assertEqual(destination.region, base_payload["region"])
        self.assertEqual(destination.u_name, base_payload["u_name"])
        self.assertEqual(destination.cost_per_week, base_payload["cost_per_week"])
        self.assertEqual(destination.description, base_payload["description"])

    def test_creation_requires_all_fields(self):
        with self.assertRaises(ValidationError):
            TravelDestination(
                **{
                    key: value
                    for key, value in self._base_destination_payload().items()
                    if key != "description"
                }
            )

    def test_invalid_preference_symbol_raises_validation_error(self):
        payload = self._base_destination_payload()
        payload["nature"] = "?"

        with self.assertRaises(ValidationError):
            TravelDestination(**payload)

    def test_preference_symbol_whitespace_is_trimmed(self):
        payload = self._base_destination_payload()
        payload["popularity"] = "  +  "
        payload["mar"] = "  o"

        destination = TravelDestination(**payload)

        self.assertEqual(destination.popularity, 0.75)
        self.assertEqual(destination.mar, 0.5)

    def test_numeric_preference_values_are_kept(self):
        payload = self._base_destination_payload()
        payload["popularity"] = 1.0
        payload["jan"] = 0
        payload["feb"] = 0.25
        payload["mar"] = 0.5
        payload["apr"] = 0.75

        destination = TravelDestination(**payload)

        self.assertEqual(destination.popularity, 1.0)
        self.assertEqual(destination.jan, 0.0)
        self.assertEqual(destination.feb, 0.25)
        self.assertEqual(destination.mar, 0.5)
        self.assertEqual(destination.apr, 0.75)

    def test_numeric_preference_out_of_range_raises_validation_error(self):
        payload = self._base_destination_payload()
        payload["popularity"] = 1.2

        with self.assertRaises(ValidationError):
            TravelDestination(**payload)

    def test_all_required_fields_must_be_present(self):
        payload = self._base_destination_payload()
        for required_field in payload:
            with self.subTest(required_field=required_field):
                invalid_payload = {k: v for k, v in payload.items() if k != required_field}
                with self.assertRaises(ValidationError):
                    TravelDestination(**invalid_payload)

    def test_cost_per_week_string_is_coerced_to_float(self):
        payload = self._base_destination_payload()
        payload["cost_per_week"] = "900.5"

        destination = TravelDestination(**payload)

        self.assertEqual(destination.cost_per_week, 900.5)
        self.assertIsInstance(destination.cost_per_week, float)

    def test_preference_symbol_is_case_sensitive(self):
        payload = self._base_destination_payload()
        payload["mar"] = "O"

        with self.assertRaises(ValidationError):
            TravelDestination(**payload)

    def test_all_preference_fields_are_converted(self):
        payload = self._base_destination_payload()
        for field_name in PREFERENCE_FIELDS:
            payload[field_name] = "++"

        destination = TravelDestination(**payload)

        for field_name in PREFERENCE_FIELDS:
            with self.subTest(field_name=field_name):
                self.assertEqual(getattr(destination, field_name), 1.0)

    def test_conversion_is_idempotent(self):
        first = TravelDestination(**self._base_destination_payload())
        second = TravelDestination(**first.model_dump())

        self.assertEqual(first.model_dump(), second.model_dump())

    def test_boundary_symbol_values_map_correctly(self):
        low_payload = self._base_destination_payload()
        high_payload = self._base_destination_payload()

        for field_name in PREFERENCE_FIELDS:
            low_payload[field_name] = "--"
            high_payload[field_name] = "++"

        low_destination = TravelDestination(**low_payload)
        high_destination = TravelDestination(**high_payload)

        for field_name in PREFERENCE_FIELDS:
            with self.subTest(boundary="low", field_name=field_name):
                self.assertEqual(getattr(low_destination, field_name), 0.0)
            with self.subTest(boundary="high", field_name=field_name):
                self.assertEqual(getattr(high_destination, field_name), 1.0)


if __name__ == "__main__":
    unittest.main()
