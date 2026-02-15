from __future__ import annotations

import os
from typing import Optional

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from recommender.embeddings.travel_csv_document_parser import TravelDataParser
from recommender.models.data_flow.recommendation_output import RecommendationBase
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class TravelVectorStore:
    """
        A vector store for travel recommendations data.
    """
    def __init__(
        self,
        db_path: str = "travel_db_index",
        csv_document_parser: Optional[TravelDataParser] = None,
    ):
        self.db_path = db_path
        self.csv_document_parser = csv_document_parser or TravelDataParser()
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
        )
        self.vector_db: Optional[FAISS] = None

    def create_embeddings(self, csv_filepath: str):
        if not os.path.exists(csv_filepath):
            logger.error("CSV file not found: %s", csv_filepath)
            raise FileNotFoundError(f"CSV file not found: {csv_filepath}")

        logger.info("Creating embeddings from %s...", csv_filepath)
        documents = self.csv_document_parser.parse_csv_to_documents(csv_filepath)
        logger.info("Processed %s valid documents.", len(documents))

        if not documents:
            logger.warning("No valid documents found. Check your CSV file.")
            return

        logger.info("Generating embeddings locally...")
        self.vector_db = FAISS.from_documents(documents, self.embeddings)
        self.vector_db.save_local(self.db_path)
        logger.info("Success. Database saved to folder: '%s'", self.db_path)

    def _load_db_to_memory(self):
        if self.vector_db is not None:
            logger.verbose("Vector database already loaded in memory.")
            return

        if not os.path.exists(self.db_path):
            logger.error("Database folder '%s' not found. Run create_embeddings() first.", self.db_path)
            raise FileNotFoundError(
                f"Database folder '{self.db_path}' not found. Run create_embeddings() first."
            )

        logger.info("Loading FAISS index from '%s'...", self.db_path)
        self.vector_db = FAISS.load_local(
            self.db_path,
            self.embeddings,
            allow_dangerous_deserialization=True,
        )

    def _check_if_db_loaded(self):
        if self.vector_db is None:
            logger.error("Vector database is not loaded. Call _load_db_to_memory() first.")
            raise RuntimeError("Vector database is not loaded. Call _load_db_to_memory() first.")

    def _convert_results_to_recommendation_outputs(
        self,
        results: list[tuple[Document, float]],
    ) -> list[RecommendationBase]:
        return [self.csv_document_parser.convert_to_recommendation_output(doc=doc, score=score, source=self.db_path) for doc, score in results]

    def search(self, query: str, k: int = 5) -> list[RecommendationBase]:
        self._load_db_to_memory()
        self._check_if_db_loaded()

        results = self.vector_db.similarity_search_with_score(query, k=k)
        logger.verbose("Search for query '%s' returned %s results.", query, len(results))
        return self._convert_results_to_recommendation_outputs(results=results)

    def search_all_ranked(self, query: str) -> list[RecommendationBase]:
        self._load_db_to_memory()
        self._check_if_db_loaded()

        total_docs = self.vector_db.index.ntotal
        results = self.vector_db.similarity_search_with_score(query, k=total_docs)
        return self._convert_results_to_recommendation_outputs(results=results)


if __name__ == "__main__":
    vector_store = TravelVectorStore()

    csv_file = "data/regionmodel_description.csv"
    vector_store.create_embeddings(csv_file)

    query = "I want to visit a place with a very good food."
    results = vector_store.search(query, k=3)

    for result in results:
        logger.info(
            "Score: %.4f, Region: %s, Content: %.100s...",
            result.score,
            result.region,
            result.content,
        )
