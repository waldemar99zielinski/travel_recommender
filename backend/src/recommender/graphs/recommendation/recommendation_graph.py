from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from recommender.graphs.recommendation.nodes.preference_extraction_node import preference_extraction_node
from recommender.graphs.recommendation.nodes.preference_validation_router import preference_validation_router
from recommender.graphs.recommendation.nodes.recommendation_generation_node import recommendation_generation_node
from recommender.graphs.recommendation.nodes.response_node import response_node

from recommender.graphs.recommendation.models import RecommendationGraphState

from utils.logger import get_logger, setup_logging


# TODO change with single base initialization
setup_logging("verbose")
logger = get_logger(__name__)


def build_recommendation_graph():
    logger.verbose("Building recommendation graph...")
    graph_builder = StateGraph(RecommendationGraphState)

    graph_builder.add_node(preference_extraction_node.__name__, preference_extraction_node)
    graph_builder.add_node(recommendation_generation_node.__name__, recommendation_generation_node)
    graph_builder.add_node(response_node.__name__, response_node)

    graph_builder.add_conditional_edges(
        preference_extraction_node.__name__,
        preference_validation_router,
        [recommendation_generation_node.__name__, response_node.__name__]
    )

    graph_builder.add_edge(START, preference_extraction_node.__name__)
    graph_builder.add_edge(recommendation_generation_node.__name__, END)
    graph_builder.add_edge(response_node.__name__, END)

    graph = graph_builder.compile()

    logger.verbose("Recommendation graph compiled successfully")

    return graph

if __name__ == "__main__":
    graph = build_recommendation_graph()
    # result = graph.invoke({"user_input": "I want to walk and explore nature, but I dislike crowded places."})
    result = graph.invoke({"user_input": "I want to sleep"})

    logger.verbose("Graph execution result:")
    logger.verbose("%r", result["extracted_preferences"])
