from __future__ import annotations

from langgraph.graph import END
from langgraph.graph import START
from langgraph.graph import StateGraph
from sqlalchemy.engine import Engine

from recommender.graphs.recommendation_v1.agents.recommendation_v1_generation_react_agent import (
    RecommendationV1ReActGenerationAgent,
)
from recommender.graphs.recommendation_v1.models import RecommendationV1GraphState
from recommender.graphs.recommendation_v1.nodes.load_session_node import (
    create_session_memory_load_node,
)
from recommender.graphs.recommendation_v1.nodes.recommendation_v1_node import (
    create_recommendation_v1_node,
)
from recommender.graphs.recommendation_v1.nodes.save_session_node import (
    create_session_memory_save_node,
)
from recommender.models.llm.llm import create_llm_chat_model
from recommender.models.llm.llm_config import LLMConfig
from storage.stores.chat_store import ChatStore
from storage.stores.travel_destination_store import TravelDestinationStore
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def build_recommendation_v1_graph(
    travel_destination_store: TravelDestinationStore,
    recommendation_session_store: ChatStore,
    db_engine: Engine,
):
    """Build recommendation_v1 graph."""
    del travel_destination_store

    logger.verbose("Building recommendation_v1 graph...")

    graph_builder = StateGraph(RecommendationV1GraphState)

    session_load_node = create_session_memory_load_node(recommendation_session_store)
    session_save_node = create_session_memory_save_node(recommendation_session_store)

    recommendation_agent = RecommendationV1ReActGenerationAgent(
        llm=create_llm_chat_model(LLMConfig()),
        db_engine=db_engine,
    )
    recommendation_v1_node = create_recommendation_v1_node(recommendation_agent)

    graph_builder.add_node(session_load_node.__name__, session_load_node)
    graph_builder.add_node(recommendation_v1_node.__name__, recommendation_v1_node)
    graph_builder.add_node(session_save_node.__name__, session_save_node)

    graph_builder.add_edge(START, session_load_node.__name__)
    graph_builder.add_edge(session_load_node.__name__, recommendation_v1_node.__name__)
    graph_builder.add_edge(recommendation_v1_node.__name__, session_save_node.__name__)
    graph_builder.add_edge(session_save_node.__name__, END)

    graph = graph_builder.compile()

    logger.info("Recommendation_v1 graph compiled")

    return graph
