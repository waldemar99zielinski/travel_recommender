from __future__ import annotations

import asyncio
from collections.abc import Awaitable
from collections.abc import Callable

from recommender.graphs.recommendation_v2.agents.recommendation_research import (
    RecommendationV2RecommendationResearchAgent,
    RecommendationV2RecommendationResearchInput,
)
from recommender.graphs.recommendation_v2.models import RecommendationV2GraphState
from recommender.graphs.recommendation_v2.models import RecommendationV2RegionResearch
from recommender.graphs.recommendation_v2.stream_events import EventType
from recommender.graphs.recommendation_v2.stream_events import StreamEventDestinationResearch
from recommender.graphs.recommendation_v2.stream_events import StreamEventDestinationResearchGeneration
from recommender.graphs.recommendation_v2.stream_events import emit_stream_event
from storage.stores.travel_destination_store import TravelDestinationStore
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def create_recommendation_research_node(
    recommendation_research_agent: RecommendationV2RecommendationResearchAgent,
    travel_destination_store: TravelDestinationStore,
) -> Callable[[RecommendationV2GraphState], Awaitable[dict[str, object]]]:
    """Create node to research final recommendations into separate state."""

    async def recommendation_research_node(
        state: RecommendationV2GraphState,
    ) -> dict[str, object]:
        if state.synthesized_user_request is None:
            raise RuntimeError(
                "Synthesized user request must be generated before researching recommendation_v2 regions"
            )

        if not state.final_recommendations:
            return {
                "travel_destinations_evaluations": state.travel_destinations_evaluations,
            }

        logger.verbose(
            "Researching %s recommendation_v2 regions for user_id=%s, session_id=%s",
            len(state.final_recommendations),
            state.session.user_id,
            state.session.session_id,
        )

        destination_ids = [
            recommendation.region_id for recommendation in state.final_recommendations
        ]
        destinations_by_id = {
            destination.id: destination
            for destination in travel_destination_store.list_by_ids(destination_ids)
        }

        recommendation_inputs: list[
            tuple[str, RecommendationV2RecommendationResearchInput]
        ] = []
        for recommendation in state.final_recommendations:
            destination = destinations_by_id.get(recommendation.region_id)
            region_description = ""
            if destination is not None:
                region_description = destination.description

            recommendation_inputs.append(
                (
                    recommendation.region_id,
                    RecommendationV2RecommendationResearchInput(
                        region_name=recommendation.region_name,
                        region_description=region_description,
                        synthesized_user_query=state.synthesized_user_request,
                        conversation=state.history,
                    ),
                )
            )

        async def research_destination(
            region_id: str,
            research_input: RecommendationV2RecommendationResearchInput,
        ) -> tuple[str, RecommendationV2RegionResearch]:
            emit_stream_event(
                EventType.DESTINATION_RESEARCH_GENERATION,
                StreamEventDestinationResearchGeneration(region_id).serialize(),
            )

            research_result = await recommendation_research_agent.invoke_async(
                research_input
            )
            destination_research = RecommendationV2RegionResearch(
                description=research_result.description,
                image_urls=research_result.image_urls,
            )

            emit_stream_event(
                EventType.DESTINATION_RESEARCH,
                StreamEventDestinationResearch(
                    region_id=region_id,
                    destination_research=destination_research,
                ).serialize(),
            )

            return region_id, destination_research

        research_results = await asyncio.gather(
            *(
                research_destination(region_id, research_input)
                for region_id, research_input in recommendation_inputs
            )
        )

        travel_destinations_evaluations: dict[str, RecommendationV2RegionResearch] = {}
        for region_id, destination_research in research_results:
            travel_destinations_evaluations[region_id] = destination_research

        logger.verbose(
            "Researched %s recommendation_v2 regions for user_id=%s, session_id=%s",
            len(travel_destinations_evaluations),
            state.session.user_id,
            state.session.session_id,
        )

        return {
            "travel_destinations_evaluations": travel_destinations_evaluations,
        }

    return recommendation_research_node
