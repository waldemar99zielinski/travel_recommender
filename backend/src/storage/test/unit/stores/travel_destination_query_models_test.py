from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[4]))

from storage.stores.query_models import TravelDestinationQuery


class TestTravelDestinationQueryModels(unittest.TestCase):
    def test_model_normalizes_nested_tool_input(self) -> None:
        query = TravelDestinationQuery.model_validate(
            {
                "text_query": "  beach sunset  ",
                "semantic_query": "  tropical beach  ",
                "filters": [
                    {
                        "field": "cost_per_week",
                        "operator": "between",
                        "min_value": "500",
                        "max_value": "1500",
                    },
                    {
                        "field": "parent_region",
                        "operator": "in",
                        "values": ["Europe", "Oceania"],
                    },
                ],
                "sort": [{"field": "popularity", "direction": "desc"}],
                "text_fields": ["description", "region", "description"],
                "limit": 7,
            }
        )

        self.assertEqual(query.text_query, "beach sunset")
        self.assertEqual(query.semantic_query, "tropical beach")
        self.assertEqual(query.text_fields, ("description", "region"))
        self.assertEqual(len(query.filters), 2)
        self.assertEqual(query.limit, 7)

    def test_model_rejects_empty_query(self) -> None:
        with self.assertRaises(ValueError):
            TravelDestinationQuery.model_validate({})

    def test_model_rejects_leading_wildcard_patterns(self) -> None:
        with self.assertRaises(ValueError):
            TravelDestinationQuery.model_validate(
                {
                    "filters": [
                        {"field": "description", "operator": "like", "value": "%beach%"},
                    ],
                }
            )

    def test_model_rejects_non_finite_numeric_values(self) -> None:
        with self.assertRaises(ValueError):
            TravelDestinationQuery.model_validate(
                {
                    "filters": [
                        {"field": "cost_per_week", "operator": "eq", "value": float("inf")},
                    ],
                }
            )

    def test_model_rejects_too_many_filters(self) -> None:
        with self.assertRaises(ValueError):
            TravelDestinationQuery.model_validate(
                {
                    "filters": [
                        {"field": "region", "operator": "eq", "value": f"Region {index}"}
                        for index in range(13)
                    ],
                }
            )


if __name__ == "__main__":
    unittest.main()
