from __future__ import annotations

from langgraph.graph import END
from langgraph.graph import START
from langgraph.graph import StateGraph

from recommender.graphs.recommendation_v0.agents.recommendation_v0_generation_react_agent import (
    RecommendationV0ReActGenerationAgent,
)
from recommender.graphs.recommendation_v0.models import RecommendationV0GraphState
from recommender.graphs.recommendation_v0.nodes.load_session_node import create_session_memory_load_node
from recommender.graphs.recommendation_v0.nodes.recommendation_v0_node import create_recommendation_v0_node
from recommender.graphs.recommendation_v0.nodes.save_session_node import create_session_memory_save_node
from recommender.models.llm.llm import create_llm_chat_model
from recommender.models.llm.llm_config import LLMConfig
from storage.stores.chat_store import ChatStore
from storage.stores.travel_destination_store import TravelDestinationStore
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def build_recommendation_v0_graph(
    travel_destination_store: TravelDestinationStore,
    recommendation_session_store: ChatStore,
):
    """Build recommendation_v0 graph."""

    del travel_destination_store

    logger.verbose("Building recommendation_v0 graph...")
    graph_builder = StateGraph(RecommendationV0GraphState)

    recommendation_agent = RecommendationV0ReActGenerationAgent(
        llm=create_llm_chat_model(LLMConfig()),
    )
    session_load_node = create_session_memory_load_node(recommendation_session_store)
    recommendation_v0_node = create_recommendation_v0_node(recommendation_agent)
    session_save_node = create_session_memory_save_node(recommendation_session_store)

    graph_builder.add_node(session_load_node.__name__, session_load_node)
    graph_builder.add_node(recommendation_v0_node.__name__, recommendation_v0_node)
    graph_builder.add_node(session_save_node.__name__, session_save_node)

    graph_builder.add_edge(START, session_load_node.__name__)
    graph_builder.add_edge(session_load_node.__name__, recommendation_v0_node.__name__)
    graph_builder.add_edge(recommendation_v0_node.__name__, session_save_node.__name__)
    graph_builder.add_edge(session_save_node.__name__, END)

    graph = graph_builder.compile()

    logger.info("Recommendation_v0 graph compiled")

    return graph
