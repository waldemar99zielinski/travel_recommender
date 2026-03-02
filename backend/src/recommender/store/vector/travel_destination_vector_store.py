from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain_ollama import OllamaEmbeddings

from recommender.common.configuration import VectorStoreConfiguration
from recommender.models.data_flow.recommendation_output import Recommendation
from recommender.store.vector.base_vector_store import BaseVectorStore
from recommender.store.vector.travel_destination_document_mapper import (
    TravelDestinationDocumentMapper,
)
from recommender.store.vector.travel_destination_vector_csv_loader import (
    TravelDestinationVectorCsvLoader,
)
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

class TravelDestinationVectorStore(BaseVectorStore):
    """FAISS-backed vector store for travel destination semantic retrieval."""

    def __init__(
        self,
        store_config: VectorStoreConfiguration | None = None,
        vector_csv_loader: TravelDestinationVectorCsvLoader | None = None,
        document_mapper: TravelDestinationDocumentMapper | None = None,
        embeddings: Embeddings | None = None,
    ) -> None:
        if store_config is None:
            raise ValueError(
                "TravelDestinationVectorStore requires VectorStoreConfiguration via store_config.",
            )

        self.store_config = store_config
        self.document_mapper = document_mapper or TravelDestinationDocumentMapper()
        self.vector_csv_loader = vector_csv_loader or TravelDestinationVectorCsvLoader(
            document_mapper=self.document_mapper,
        )
        self.embeddings = embeddings or OllamaEmbeddings(model="nomic-embed-text")
        self.vector_db: FAISS | None = None

    def build_from_csv(self, csv_file_path: str) -> None:
        if not os.path.exists(csv_file_path):
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")

        documents = self.vector_csv_loader.load(csv_file_path)
        if not documents:
            logger.warning("No valid documents produced from %s", csv_file_path)
            return

        vector_db = FAISS.from_documents(documents, self.embeddings)
        self.vector_db = vector_db
        vector_db.save_local(self.store_config.db_path)
        logger.info(
            "Vector index built with %s documents at %s",
            len(documents),
            self.store_config.db_path,
        )

    def load(self) -> None:
        if self.vector_db is not None:
            return

        if not os.path.exists(self.store_config.db_path):
            raise FileNotFoundError(
                f"Database folder '{self.store_config.db_path}' not found. Run build_from_csv() first."
            )

        self.vector_db = FAISS.load_local(
            self.store_config.db_path,
            self.embeddings,
            allow_dangerous_deserialization=True,
        )

    def is_loaded(self) -> bool:
        return self.vector_db is not None

    def size(self) -> int:
        vector_db = self._get_vector_db()
        return int(vector_db.index.ntotal)

    def search(self, query: str, k: int = 5) -> list[Recommendation]:
        vector_db = self._get_vector_db()
        results = vector_db.similarity_search_with_score(query, k=k)
        return [
            self.document_mapper.to_recommendation(doc=doc, embedding_score=score)
            for doc, score in results
        ]

    def search_all_ranked(self, query: str) -> list[Recommendation]:
        vector_db = self._get_vector_db()
        total_docs = int(vector_db.index.ntotal)
        results = vector_db.similarity_search_with_score(query, k=total_docs)
        return [
            self.document_mapper.to_recommendation(doc=doc, embedding_score=score)
            for doc, score in results
        ]

    def _get_vector_db(self) -> FAISS:
        self.load()
        if self.vector_db is None:
            raise RuntimeError("Vector database is not loaded. Call load() first.")
        return self.vector_db


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[4]
    csv_path = str(project_root / "data" / "regionmodel_with_detailed_descriptions.csv")
    store_config = VectorStoreConfiguration(
        db_path=str(project_root / "store_data" / "travel_destinations_vector_index"),
    )
    query = "beach ocean sunshine"

    store = TravelDestinationVectorStore(store_config=store_config)
    store.build_from_csv(csv_path)
    logger.info("Vector store loaded=%s size=%s", store.is_loaded(), store.size())

    for recommendation in store.search(query, k=3):
        logger.info(
            "Result u_name=%s score=%.4f region=%s",
            recommendation.u_name,
            recommendation.embedding_score,
            recommendation.region,
        )
