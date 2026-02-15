from langgraph.graph import StateGraph, START, END

from recommender.agents.preference_extraction.preference_extraction_agent import PreferenceExtractionAgent
from recommender.embeddings.travel_vector_store import TravelVectorStore

from recommender.graphs.recommendation.nodes.preference_extraction_node import create_preference_extraction_node 
from recommender.graphs.recommendation.nodes.preference_validation_router import (
    ROUTE_RECOMMENDATION_GENERATION,
    ROUTE_RESPONSE,
    preference_validation_router,
)
from recommender.graphs.recommendation.nodes.recommendation_generation_node import create_recommendation_generation_node
from recommender.graphs.recommendation.nodes.response_node import create_response_node
from recommender.graphs.recommendation.models import RecommendationGraphState

from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

def build_recommendation_graph():
    logger.verbose("Building recommendation graph...")
    graph_builder = StateGraph(RecommendationGraphState)

    preference_extraction_agent = PreferenceExtractionAgent.builder().build()

    preference_extraction_node = create_preference_extraction_node(
        preference_extraction_agent
    )

    travel_vector_store = TravelVectorStore()

    recommendation_generation_node = create_recommendation_generation_node(
        travel_vector_store 
    )

    response_node = create_response_node()

    preference_extraction_node_name = create_preference_extraction_node.__name__
    recommendation_generation_node_name = create_recommendation_generation_node.__name__
    response_node_name = create_response_node.__name__

    graph_builder.add_node(preference_extraction_node_name, preference_extraction_node)
    graph_builder.add_node(recommendation_generation_node_name, recommendation_generation_node)
    graph_builder.add_node(response_node_name, response_node)

    graph_builder.add_conditional_edges(
        preference_extraction_node_name,
        preference_validation_router,
        {
            ROUTE_RECOMMENDATION_GENERATION: recommendation_generation_node_name,
            ROUTE_RESPONSE: response_node_name,
        },
    )

    graph_builder.add_edge(START, preference_extraction_node_name)
    graph_builder.add_edge(recommendation_generation_node_name, response_node_name)
    graph_builder.add_edge(response_node_name, END)

    graph = graph_builder.compile()

    logger.verbose("Recommendation graph compiled successfully")

    return graph

if __name__ == "__main__":
    graph = build_recommendation_graph()
    result = graph.invoke({"user_input": "I want to walk and explore nature, but I dislike crowded places."})
    # result = graph.invoke({"user_input": "I want to sleep"})

    logger.verbose("Graph execution result:\n%r", result)
    # logger.verbose("%r", result)
