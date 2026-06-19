from __future__ import annotations

import sys
import unittest
from pathlib import Path
from uuid import UUID

sys.path.append(str(Path(__file__).resolve().parents[4]))

from storage.configuration import MigrationConfiguration
from storage.configuration import StorageConfiguration
from storage.configuration import StorageEngineConfiguration
from storage.models.survey_result import SurveyResult
from storage.models.survey_result import SurveyResultsData
from storage.storage import Storage
from storage.test.utils import FakeTextEmbeddingModel
from storage.test.utils import build_db_url_with_schema_search_path
from storage.test.utils import create_schema
from storage.test.utils import drop_schema
from storage.test.utils import generate_schema_name

DEVELOPMENT_BASE_DB_URL = (
    "postgresql+psycopg://"
    "hybrid_dev:change_me_dev_password@localhost:5432/recommender"
)


class TestSurveyStoreE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base_db_url = DEVELOPMENT_BASE_DB_URL
        cls.embedding_model = FakeTextEmbeddingModel(dimensions=8)

    def setUp(self) -> None:
        self.schema_name = generate_schema_name(prefix="test_survey_store")
        create_schema(self.base_db_url, self.schema_name)
        schema_db_url = build_db_url_with_schema_search_path(self.base_db_url, self.schema_name)
        self.storage_configuration = StorageConfiguration(
            engine=StorageEngineConfiguration(db_url=schema_db_url),
            migrations=MigrationConfiguration(enabled=True),
            schema_name=self.schema_name,
        )

    def tearDown(self) -> None:
        drop_schema(self.base_db_url, self.schema_name)

    def test_save_result_returns_persisted_model_with_generated_id(self) -> None:
        user_id = UUID("11111111-1111-1111-1111-111111111111")
        session_id = UUID("22222222-2222-2222-2222-222222222222")

        with Storage(self.storage_configuration, embedding_model=self.embedding_model) as storage:
            saved = storage.survey.save_result(
                SurveyResult(
                    user_id=user_id,
                    session_id=session_id,
                    results=SurveyResultsData(scores={1: 4.5, 2: 3.0}),
                    comment="helpful recommendations",
                )
            )

            self.assertIsNotNone(saved.id)
            self.assertEqual(saved.user_id, user_id)
            self.assertEqual(saved.session_id, session_id)
            self.assertEqual(saved.results.scores, {1: 4.5, 2: 3.0})
            self.assertEqual(saved.comment, "helpful recommendations")

            persisted_results = storage.survey.list_results_by_session(session_id)

        self.assertEqual(len(persisted_results), 1)
        self.assertEqual(persisted_results[0].id, saved.id)
        self.assertEqual(persisted_results[0].results.scores, {1: 4.5, 2: 3.0})


if __name__ == "__main__":
    unittest.main()
