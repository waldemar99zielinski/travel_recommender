from __future__ import annotations

from api.app import create_app
from api.core.configuration import load_api_configuration
from api.services.recommendation_v2_service import RecommendationV2Service
from api.services.session_service import SessionService
from embeddings.loader import load_text_embedding_model
from recommender.graphs.recommendation_v2 import build_recommendation_v2_graph
from storage.configuration import load_storage_configuration
from storage.storage import Storage
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

logger.info("Starting API setup")

configuration = load_api_configuration()
logger.info(
    "API configuration loaded: env=%s, log_level=%s, host=%s, port=%d",
    configuration.env.value,
    configuration.log_level.value,
    configuration.host,
    configuration.port,
)

logger.info("Initializing embedding model")
embedding_model = load_text_embedding_model()

logger.info("Initializing storage")
storage_configuration = load_storage_configuration()
storage = Storage(storage_configuration, embedding_model=embedding_model)

logger.info("Compiling recommendation_v2 graph")
recommendation_v2_graph = build_recommendation_v2_graph(
    travel_destination_store=storage.travel_destinations,
    recommendation_session_store=storage.chat,
)

recommendation_v2_service = RecommendationV2Service(
    recommendation_graph=recommendation_v2_graph,
)
session_service = SessionService(
    chat_store=storage.chat,
    travel_destination_store=storage.travel_destinations,
)

app = create_app(
    configuration=configuration,
    embedding_model=embedding_model,
    storage=storage,
    recommendation_v2_service=recommendation_v2_service,
    session_service=session_service,
)

logger.info("API setup completed")
