from __future__ import annotations

import unittest

from recommender.graphs.recommendation_v2.agents.filter_extraction.regions.models import (
    RecommendationV2RegionsFilterExtractionInput,
)
from recommender.graphs.recommendation_v2.agents.filter_extraction.regions.models import (
    RecommendationV2RegionsFilterExtractionResult,
)
from recommender.graphs.recommendation_v2.filter_models import (
    RecommendationV2RegionFilter,
    RecommendationV2SeasonalityFilter,
    RecommendationV2TravelDestinationFilter,
)
from recommender.graphs.recommendation_v2.models import RecommendationV2GraphState
from recommender.graphs.recommendation_v2.nodes.extract_regions_filter_node import (
    create_extract_regions_filter_node,
)
from recommender.models.session.session import Session


class _StubRegionsFilterExtractionAgent:
    def __init__(self, result: RecommendationV2RegionsFilterExtractionResult) -> None:
        self.result = result
        self.last_input: RecommendationV2RegionsFilterExtractionInput | None = None

    def invoke(
        self,
        inputs: RecommendationV2RegionsFilterExtractionInput,
    ) -> RecommendationV2RegionsFilterExtractionResult:
        self.last_input = inputs
        return self.result


class TestExtractRegionsFilterNode(unittest.TestCase):
    def test_request_region_ids_override_agent_regions_and_preserve_previous_filter(self) -> None:
        previous_filter = RecommendationV2TravelDestinationFilter(
            regions=[
                RecommendationV2RegionFilter(
                    field_name="parent_region",
                    region_name="Southern Europe",
                    type="include",
                )
            ],
            seasonality=RecommendationV2SeasonalityFilter(season="summer"),
        )
        agent = _StubRegionsFilterExtractionAgent(
            RecommendationV2RegionsFilterExtractionResult(
                regions=[
                    RecommendationV2RegionFilter(
                        field_name="parent_region",
                        region_name="Southern Europe",
                        type="include",
                    ),
                    RecommendationV2RegionFilter(
                        field_name="region",
                        region_name="Italy and Malta",
                        type="include",
                    ),
                ]
            )
        )
        node = create_extract_regions_filter_node(agent)

        result = node(
            RecommendationV2GraphState(
                session=Session(user_id="user-1", session_id="session-1"),
                user_request="same area, but exclude Italy and Malta",
                included_regions_ids_from_request=[],
                excluded_regions_ids_from_request=["Italy and Malta"],
                previously_extracted_travel_destination_filter=previous_filter,
                history=[],
            )
        )

        self.assertIsNotNone(agent.last_input)
        self.assertEqual(
            agent.last_input.current_user_request,
            "same area, but exclude Italy and Malta",
        )

        extracted_region_filters = result["extracted_region_filters"]
        self.assertEqual(
            extracted_region_filters,
            [
                RecommendationV2RegionFilter(
                    field_name="parent_region",
                    region_name="Southern Europe",
                    type="include",
                ),
                RecommendationV2RegionFilter(
                    field_name="region",
                    region_name="Italy and Malta",
                    type="exclude",
                ),
            ],
        )


if __name__ == "__main__":
    unittest.main()
