from __future__ import annotations

from typing import Any

from langgraph.graph import END
from langgraph.graph import START
from langgraph.graph import StateGraph

from recommender.agents.query_synthesis_and_validation.query_synthesis_and_validation_agent import (
    RecommendationQuerySynthesisAndValidationAgent,
)
from recommender.agents.recommendation_generation.recommendation_v3_generation_react_agent import (
    RecommendationV3ReActGenerationAgent,
)
from recommender.agents.response_generation.recommendation_v3_response_generation_agent import (
    RecommendationV3ResponseGenerationAgent,
)
from recommender.graphs.recommendation_v3.models import RecommendationV3GraphState
from recommender.graphs.recommendation_v3.models import QuerySynthesisRoutingOutcome
from recommender.graphs.recommendation_v3.nodes.query_synthesis_and_validation_node import (
    create_query_synthesis_and_validation_node,
)
from recommender.graphs.recommendation_v3.nodes.recommendation_generation_node import (
    create_recommendation_generation_node,
)
from recommender.graphs.recommendation_v3.nodes.response_generation_node import (
    create_response_generation_node,
)
from recommender.graphs.recommendation_v3.nodes.session_memory_load_node import (
    create_session_memory_load_node,
)
from recommender.graphs.recommendation_v3.nodes.session_memory_update_node import (
    create_session_memory_update_node,
)
from storage.stores.recommendation_session_store import RecommendationSessionStore
from storage.stores.travel_destination_store import TravelDestinationStore
from utils.logger import LoggerManager

logger: Any = LoggerManager.get_logger(__name__)


def _outcome_router(state: RecommendationV3GraphState) -> str:
    outcome = state.routing_outcome
    logger.verbose("_outcome_router: routing outcome=%s", outcome)
    if outcome == QuerySynthesisRoutingOutcome.RUN_NEW_RECOMMENDATION:
        return QuerySynthesisRoutingOutcome.RUN_NEW_RECOMMENDATION.value
    if outcome == QuerySynthesisRoutingOutcome.OUTSIDE_OF_RECOMMENDER_SCOPE:
        return QuerySynthesisRoutingOutcome.OUTSIDE_OF_RECOMMENDER_SCOPE.value
    logger.verbose("_outcome_router: defaulting to not_enough_information_provided")
    return QuerySynthesisRoutingOutcome.NOT_ENOUGH_INFORMATION_PROVIDED.value


def build_recommendation_v3_graph(
    travel_destination_store: TravelDestinationStore,
    recommendation_session_store: RecommendationSessionStore,
):
    """Build a placeholder recommendation_v3 graph from the current proposal."""

    logger.verbose("Building recommendation_v3 graph...")
    graph_builder = StateGraph(RecommendationV3GraphState)

    query_synthesis_and_validation_agent = RecommendationQuerySynthesisAndValidationAgent.builder().build()
    recommendation_v3_generation_agent = (
        RecommendationV3ReActGenerationAgent.builder(travel_destination_store).build()
    )
    session_memory_load_node = create_session_memory_load_node(recommendation_session_store)
    query_synthesis_and_validation_node = create_query_synthesis_and_validation_node(
        query_synthesis_and_validation_agent,
    )
    recommendation_generation_node = create_recommendation_generation_node(
        recommendation_v3_generation_agent,
    )
    response_generation_agent = RecommendationV3ResponseGenerationAgent.builder().build()
    response_generation_node = create_response_generation_node(response_generation_agent)
    session_memory_update_node = create_session_memory_update_node(recommendation_session_store)

    graph_builder.add_node(create_session_memory_load_node.__name__, session_memory_load_node)
    graph_builder.add_node(
        create_query_synthesis_and_validation_node.__name__,
        query_synthesis_and_validation_node,
    )
    graph_builder.add_node(
        create_recommendation_generation_node.__name__,
        recommendation_generation_node,
    )
    graph_builder.add_node(create_response_generation_node.__name__, response_generation_node)
    graph_builder.add_node(create_session_memory_update_node.__name__, session_memory_update_node)

    graph_builder.add_edge(START, create_session_memory_load_node.__name__)
    graph_builder.add_edge(
        create_session_memory_load_node.__name__,
        create_query_synthesis_and_validation_node.__name__,
    )
    graph_builder.add_conditional_edges(
        create_query_synthesis_and_validation_node.__name__,
        _outcome_router,
        {
            QuerySynthesisRoutingOutcome.OUTSIDE_OF_RECOMMENDER_SCOPE.value: create_response_generation_node.__name__,
            QuerySynthesisRoutingOutcome.NOT_ENOUGH_INFORMATION_PROVIDED.value: create_response_generation_node.__name__,
            QuerySynthesisRoutingOutcome.RUN_NEW_RECOMMENDATION.value: create_recommendation_generation_node.__name__,
        },
    )
    graph_builder.add_edge(
        create_recommendation_generation_node.__name__,
        create_response_generation_node.__name__,
    )
    graph_builder.add_edge(
        create_response_generation_node.__name__,
        create_session_memory_update_node.__name__,
    )
    graph_builder.add_edge(create_session_memory_update_node.__name__, END)

    graph = graph_builder.compile()
    logger.verbose("recommendation_v3 graph compiled successfully")
    return graph
