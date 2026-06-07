from __future__ import annotations

from langgraph.graph import END
from langgraph.graph import START
from langgraph.graph import StateGraph
from recommender.graphs.recommendation_v2.agents.filter_extraction.filter_extraction_agent import (
    RecommendationV2FilterExtractionAgent,
)
from recommender.graphs.recommendation_v2.agents.query_synthesis.query_synthesis_agent import (
    RecommendationV2SynthesizedUserRequestAgent,
)
from recommender.graphs.recommendation_v2.agents.request_routing.request_routing_agent import (
    RecommendationV2RequestRoutingAgent,
)
from recommender.graphs.recommendation_v2.agents.response_generation.need_more_information.agent import (
    RecommendationV2NeedMoreInformationResponseGenerationAgent,
)
from recommender.graphs.recommendation_v2.agents.response_generation.no_results_for_recommendation.agent import (
    RecommendationV2NoResultsForRecommendationResponseGenerationAgent,
)
from recommender.graphs.recommendation_v2.agents.response_generation.out_of_scope.agent import (
    RecommendationV2OutOfScopeResponseGenerationAgent,
)
from recommender.graphs.recommendation_v2.agents.response_generation.recommendation_generated.agent import (
    RecommendationV2RecommendationGeneratedResponseGenerationAgent,
)
from recommender.graphs.recommendation_v2.models import RecommendationV2GraphState
from recommender.graphs.recommendation_v2.nodes.extract_travel_filters_node import (
    create_extract_travel_filters_node,
)
from recommender.graphs.recommendation_v2.nodes.load_session_node import (
    create_session_memory_load_node,
)
from recommender.graphs.recommendation_v2.nodes.need_more_information_response_generation_node import (
    create_need_more_information_response_generation_node,
)
from recommender.graphs.recommendation_v2.nodes.out_of_scope_response_generation_node import (
    create_out_of_scope_response_generation_node,
)
from recommender.graphs.recommendation_v2.nodes.recommendation_generation_node import (
    create_recommendation_generation_node,
)
from recommender.graphs.recommendation_v2.nodes.recommendation_response_generation_node import (
    create_recommendation_response_generation_node,
)
from recommender.graphs.recommendation_v2.nodes.request_routing_node import (
    create_request_routing_node,
)
from recommender.graphs.recommendation_v2.nodes.save_session_node import (
    create_session_memory_save_node,
)
from recommender.graphs.recommendation_v2.nodes.synthesize_user_request_node import (
    create_synthesize_user_request_node,
)
from recommender.models.llm.llm import create_llm_chat_model
from recommender.models.llm.llm_config import LLMConfig
from storage.stores.chat_store import ChatStore
from storage.stores.travel_destination_store import TravelDestinationStore
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def _request_routing_router(state: RecommendationV2GraphState) -> str:
    if state.request_routing_decision is None:
        raise RuntimeError(
            "Request routing decision must be available before routing the recommendation_v2 graph"
        )

    return state.request_routing_decision


def build_recommendation_v2_graph(
    travel_destination_store: TravelDestinationStore,
    recommendation_session_store: ChatStore,
):
    """Build the recommendation_v2 graph."""

    logger.verbose("Building recommendation_v2 graph...")

    graph_builder = StateGraph(RecommendationV2GraphState)
    llm = create_llm_chat_model(LLMConfig())

    session_load_node = create_session_memory_load_node(recommendation_session_store)
    request_routing_node = create_request_routing_node(
        RecommendationV2RequestRoutingAgent(llm=llm),
    )
    synthesize_user_request_node = create_synthesize_user_request_node(
        RecommendationV2SynthesizedUserRequestAgent(llm=llm),
    )
    extract_travel_filters_node = create_extract_travel_filters_node(
        RecommendationV2FilterExtractionAgent(llm=llm),
    )
    recommendation_generation_node = create_recommendation_generation_node(
        travel_destination_store,
    )
    recommendation_response_generation_node = create_recommendation_response_generation_node(
        RecommendationV2RecommendationGeneratedResponseGenerationAgent(llm=llm),
        RecommendationV2NoResultsForRecommendationResponseGenerationAgent(llm=llm),
    )
    need_more_information_response_generation_node = (
        create_need_more_information_response_generation_node(
            RecommendationV2NeedMoreInformationResponseGenerationAgent(llm=llm),
        )
    )
    out_of_scope_response_generation_node = create_out_of_scope_response_generation_node(
        RecommendationV2OutOfScopeResponseGenerationAgent(llm=llm),
    )
    session_save_node = create_session_memory_save_node(recommendation_session_store)

    graph_builder.add_node(session_load_node.__name__, session_load_node)
    graph_builder.add_node(request_routing_node.__name__, request_routing_node)
    graph_builder.add_node(synthesize_user_request_node.__name__, synthesize_user_request_node)
    graph_builder.add_node(extract_travel_filters_node.__name__, extract_travel_filters_node)
    graph_builder.add_node(recommendation_generation_node.__name__, recommendation_generation_node)
    graph_builder.add_node(
        recommendation_response_generation_node.__name__,
        recommendation_response_generation_node,
    )
    graph_builder.add_node(
        need_more_information_response_generation_node.__name__,
        need_more_information_response_generation_node,
    )
    graph_builder.add_node(
        out_of_scope_response_generation_node.__name__,
        out_of_scope_response_generation_node,
    )
    graph_builder.add_node(session_save_node.__name__, session_save_node)

    # edges
    graph_builder.add_edge(START, session_load_node.__name__)

    graph_builder.add_edge(session_load_node.__name__, request_routing_node.__name__)

    graph_builder.add_conditional_edges(
        request_routing_node.__name__,
        _request_routing_router,
        {
            "new_recommendation_run": synthesize_user_request_node.__name__,
            "need_more_information_from_user": need_more_information_response_generation_node.__name__,
            "out_of_system_scope": out_of_scope_response_generation_node.__name__,
        },
    )

    graph_builder.add_edge(
        need_more_information_response_generation_node.__name__,
        session_save_node.__name__,
    )
    graph_builder.add_edge(
        out_of_scope_response_generation_node.__name__,
        session_save_node.__name__,
    )

    graph_builder.add_edge(synthesize_user_request_node.__name__, extract_travel_filters_node.__name__)
    graph_builder.add_edge(extract_travel_filters_node.__name__, recommendation_generation_node.__name__)
    graph_builder.add_edge(
        recommendation_generation_node.__name__,
        recommendation_response_generation_node.__name__,
    )

    graph_builder.add_edge(
        recommendation_response_generation_node.__name__,
        session_save_node.__name__,
    )
    graph_builder.add_edge(session_save_node.__name__, END)

    graph = graph_builder.compile()

    logger.info("Recommendation_v2 graph compiled")

    return graph
