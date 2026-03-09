from langgraph.graph import END
from langgraph.graph import START
from langgraph.graph import StateGraph

from recommender.common.configuration import Configuration

from recommender.agents.preference_extraction.user_interest_preference_extraction_agent import UserInterestPreferenceExtractionAgent
from recommender.agents.preference_extraction.user_logistical_preference_extraction_agent import UserLogisticalPreferenceExtractionAgent
from recommender.agents.response_generation.recommendation_response_generation_agent import (
    RecommendationResponseGenerationAgent,
)
from recommender.store.vector.travel_destination_vector_store import (
    TravelDestinationVectorStore,
)

from recommender.graphs.recommendation.nodes.preference_extraction_node import create_preference_extraction_node 
from recommender.graphs.recommendation.nodes.preference_validation_router import (
    ROUTE_RECOMMENDATION_GENERATION,
    ROUTE_RESPONSE,
    preference_validation_router,
)
from recommender.graphs.recommendation.nodes.recommendation_generation_node import create_recommendation_generation_node
from recommender.graphs.recommendation.nodes.recommendation_ranking_node import create_recommendation_ranking_node
from recommender.graphs.recommendation.nodes.response_node import create_response_node
from recommender.graphs.recommendation.nodes.session_memory_load_node import create_session_memory_load_node
from recommender.graphs.recommendation.nodes.session_memory_update_node import create_session_memory_update_node
from recommender.graphs.recommendation.models import RecommendationGraphState
from recommender.models.session.session import Session
from recommender.store.sql.travel_destination_store import SqlStore
from recommender.store.sql.tables.travel_destination_table import TravelDestinationTable

from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


def build_recommendation_graph(
    travel_vector_store: TravelDestinationVectorStore,
    sql_store: SqlStore,
):
    logger.verbose("Building recommendation graph...")
    graph_builder = StateGraph(RecommendationGraphState)

    user_interest_preference_extraction_agent = UserInterestPreferenceExtractionAgent.builder().build()
    user_logistical_preference_extraction_agent = UserLogisticalPreferenceExtractionAgent.builder().build()
    recommendation_response_generation_agent = RecommendationResponseGenerationAgent.builder().build()


    preference_extraction_node = create_preference_extraction_node(
        user_interest_preference_extraction_agent,
        user_logistical_preference_extraction_agent,
    )

    recommendation_generation_node = create_recommendation_generation_node(
        travel_vector_store 
    )
    recommendation_ranking_node = create_recommendation_ranking_node(sql_store)

    response_node = create_response_node(recommendation_response_generation_agent)

    session_memory_load_node = create_session_memory_load_node(sql_store)
    session_memory_update_node = create_session_memory_update_node(sql_store)

    graph_builder.add_node(create_preference_extraction_node.__name__, preference_extraction_node)
    graph_builder.add_node(create_recommendation_generation_node.__name__, recommendation_generation_node)
    graph_builder.add_node(create_recommendation_ranking_node.__name__, recommendation_ranking_node)
    graph_builder.add_node(create_response_node.__name__, response_node)
    graph_builder.add_node(create_session_memory_load_node.__name__, session_memory_load_node)
    graph_builder.add_node(create_session_memory_update_node.__name__, session_memory_update_node)

    graph_builder.add_conditional_edges(
        create_preference_extraction_node.__name__,
        preference_validation_router,
        {
            ROUTE_RECOMMENDATION_GENERATION: create_recommendation_generation_node.__name__,
            ROUTE_RESPONSE: create_response_node.__name__,
        },
    )

    graph_builder.add_edge(START, create_session_memory_load_node.__name__)
    graph_builder.add_edge(create_session_memory_load_node.__name__, create_preference_extraction_node.__name__)
    graph_builder.add_edge(
        create_recommendation_generation_node.__name__,
        create_recommendation_ranking_node.__name__,
    )
    graph_builder.add_edge(create_recommendation_ranking_node.__name__, create_response_node.__name__)
    graph_builder.add_edge(create_response_node.__name__, create_session_memory_update_node.__name__)
    graph_builder.add_edge(create_session_memory_update_node.__name__, END)

    graph = graph_builder.compile()

    logger.verbose("Recommendation graph compiled successfully")

    return graph

if __name__ == "__main__":

    config = Configuration() 

    sql_store = SqlStore(store_config=config.stores.sql)
    sql_store.load()
    if sql_store.size(TravelDestinationTable) == 0:
        sql_store.load_travel_destinations_data_from_csv(
            str(config.stores.bootstrap.seed_csv_path),
            mode="replace",
        )

    travel_vector_store = TravelDestinationVectorStore(store_config=config.stores.vector)

    # travel_vector_store.build_from_csv(config.stores.bootstrap.seed_csv_path)
    travel_vector_store.load()

    graph = build_recommendation_graph(
        travel_vector_store=travel_vector_store,
        sql_store=sql_store,
    )
    
    session = Session(user_id="user_1", session_id="session_1")
    result = graph.invoke({
        "session": session,
        "user_input": "I want to walk and explore nature in August with 200 euro, but I dislike crowded places."
    })
    # result = graph.invoke({"user_input": "I want to sleep"})

    parsed_result  = RecommendationGraphState.model_validate(result)

    logger.verbose("Graph execution result:\n%r", parsed_result)
    # logger.verbose("%r", parsed_result)
