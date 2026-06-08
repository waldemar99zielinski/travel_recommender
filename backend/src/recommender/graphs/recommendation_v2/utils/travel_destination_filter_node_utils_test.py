from __future__ import annotations

import unittest

from recommender.graphs.recommendation_v2.filter_models import CostTerm
from recommender.graphs.recommendation_v2.filter_models import RecommendationV2BudgetFilter
from recommender.graphs.recommendation_v2.filter_models import RecommendationV2RegionFilter
from recommender.graphs.recommendation_v2.filter_models import RecommendationV2SeasonalityFilter
from recommender.graphs.recommendation_v2.filter_models import RecommendationV2TravelDestinationFilter
from recommender.graphs.recommendation_v2.utils.travel_destination_filter_node_utils import (
    compose_travel_destination_filter,
)


class TestComposeTravelDestinationFilter(unittest.TestCase):
    def test_uses_fallback_per_missing_category(self) -> None:
        fallback = RecommendationV2TravelDestinationFilter(
            parent_region_filters=[
                RecommendationV2RegionFilter(
                    field_name="parent_region",
                    region_name="Southern Europe",
                    type="include",
                )
            ],
            direct_region_filters=[
                RecommendationV2RegionFilter(
                    field_name="region",
                    region_name="Spain",
                    type="exclude",
                )
            ],
            seasonality=RecommendationV2SeasonalityFilter(months=["jun"]),
            budget=RecommendationV2BudgetFilter(
                cost_term=CostTerm.model_validate({"inferred_level": "medium"}),
            ),
        )

        composed = compose_travel_destination_filter(
            extracted_parent_region_filters=[],
            extracted_direct_region_filters=[
                RecommendationV2RegionFilter(
                    field_name="region",
                    region_name="Greece",
                    type="include",
                )
            ],
            extracted_seasonality_filter=None,
            extracted_budget_filter=RecommendationV2BudgetFilter(),
            fallback=fallback,
        )

        self.assertIsNot(composed, fallback)
        self.assertEqual(
            composed.serialize(),
            {
                "parent_region_filters": [
                    {
                        "field_name": "parent_region",
                        "region_name": "Southern Europe",
                        "type": "include",
                    }
                ],
                "direct_region_filters": [
                    {
                        "field_name": "region",
                        "region_name": "Greece",
                        "type": "include",
                    }
                ],
                "seasonality": {
                    "months": ["jun"],
                },
                "budget": {
                    "cost_term": {
                        "inferred_level": "medium",
                    }
                },
            },
        )


if __name__ == "__main__":
    unittest.main()
