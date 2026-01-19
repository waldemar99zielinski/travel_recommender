import logging
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from recommender.models.data_flow.user_preferences import UserPreferences
from recommender.agents.preference_extraction.preference_extraction_agent import PreferenceExtractionAgent

logger = logging.getLogger(__name__)

class GraphState(TypedDict):
    user_input: str
    extracted_preferences: UserPreferences

def preference_extraction_node(state: GraphState) -> GraphState:
    agent = PreferenceExtractionAgent.builder().build()
    
    user_preferences = agent.invoke(state["user_input"])
    return GraphState(extracted_preferences=user_preferences)

def build_recommendation_graph():
    logger.debug("Building recommendation graph...")
    graph_builder = StateGraph(GraphState)

    graph_builder.add_edge(START, preference_extraction_node.__name__)
    graph_builder.add_edge(preference_extraction_node.__name__, END)
    graph_builder.add_node(preference_extraction_node.__name__, preference_extraction_node)

    graph = graph_builder.compile()

    logger.debug("Recommendation graph compiledsuccessfully.")

    return graph

if __name__ == "__main__":
    # TODO make reasonable logger
    logging.basicConfig(level=logging.DEBUG)
    graph = build_recommendation_graph()
    result = graph.invoke({"user_input": "I want to walk and explore nature, but I dislike crowded places."})

    print("Graph invocation result:")
    print(result["extracted_preferences"])