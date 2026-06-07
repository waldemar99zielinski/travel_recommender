from __future__ import annotations

import unittest

from recommender.graphs.recommendation_v2.filter_models import CostTerm
from recommender.graphs.recommendation_v2.filter_models import RecommendationV2BudgetFilter
from recommender.graphs.recommendation_v2.filter_models import RecommendationV2RegionFilter
from recommender.graphs.recommendation_v2.filter_models import RecommendationV2SeasonalityFilter
from recommender.graphs.recommendation_v2.filter_models import RecommendationV2TravelDestinationFilter


class TestRecommendationV2TravelDestinationFilter(unittest.TestCase):
    def test_serializes_into_category_object(self) -> None:
        travel_destination_filter = RecommendationV2TravelDestinationFilter(
            regions=[
                RecommendationV2RegionFilter(
                    field_name="parent_region",
                    region_name="Southern Europe",
                    type="include",
                )
            ],
            seasonality=RecommendationV2SeasonalityFilter(
                season="summer",
                months=["jun", "jul"],
            ),
            budget=RecommendationV2BudgetFilter(
                cost_term=CostTerm.model_validate({"inferred_level": "medium"}),
            ),
        )

        self.assertEqual(
            travel_destination_filter.serialize(),
            {
                "regions": [
                    {
                        "field_name": "parent_region",
                        "region_name": "Southern Europe",
                        "type": "include",
                    }
                ],
                "seasonality": {
                    "season": "summer",
                    "months": ["jun", "jul"],
                },
                "budget": {
                    "cost_term": {
                        "inferred_level": "medium",
                    }
                },
            },
        )

    def test_accepts_legacy_flat_payload(self) -> None:
        travel_destination_filter = RecommendationV2TravelDestinationFilter.model_validate(
            {
                "parent_region": "Caribbean",
                "season": "winter",
                "months": ["dec"],
                "max_cost_per_week": 700,
            }
        )

        self.assertEqual(travel_destination_filter.regions[0].region_name, "Caribbean")
        self.assertEqual(travel_destination_filter.seasonality.season, "winter")
        self.assertEqual(travel_destination_filter.seasonality.months, ["dec"])
        self.assertEqual(travel_destination_filter.budget.max_cost_per_week, 700)


if __name__ == "__main__":
    unittest.main()
