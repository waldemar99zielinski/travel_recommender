from __future__ import annotations

from typing import Callable

from recommender.embeddings.travel_vector_store import TravelVectorStore
from recommender.graphs.recommendation.models import RecommendationGraphState
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)