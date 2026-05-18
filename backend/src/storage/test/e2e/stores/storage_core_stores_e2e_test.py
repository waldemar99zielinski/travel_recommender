from __future__ import annotations

import sys
import unittest
from pathlib import Path
from uuid import UUID

sys.path.append(str(Path(__file__).resolve().parents[4]))

from storage.configuration import MigrationConfiguration
from storage.configuration import StorageConfiguration
from storage.configuration import StorageEngineConfiguration
from storage.models.recommendation_session_memory import RecommendationSessionMemoryRecord
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


class TestStorageCoreStoresE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base_db_url = DEVELOPMENT_BASE_DB_URL
        cls.embedding_model = FakeTextEmbeddingModel(dimensions=8)

    def setUp(self) -> None:
        self.schema_name = generate_schema_name(prefix="test_storage_core_stores")
        create_schema(self.base_db_url, self.schema_name)
        schema_db_url = build_db_url_with_schema_search_path(self.base_db_url, self.schema_name)
        self.storage_configuration = StorageConfiguration(
            engine=StorageEngineConfiguration(db_url=schema_db_url),
            migrations=MigrationConfiguration(enabled=True),
            schema_name=self.schema_name,
        )

    def tearDown(self) -> None:
        drop_schema(self.base_db_url, self.schema_name)

    def test_storage_metadata_store_crud_and_embedding_contract(self) -> None:
        with Storage(self.storage_configuration, embedding_model=self.embedding_model) as storage:
            self.assertEqual(storage.storage_metadata.get_value("embedding_dimension"), "8")

            storage.storage_metadata.upsert("custom_key", "alpha")
            self.assertEqual(storage.storage_metadata.get_value("custom_key"), "alpha")

            storage.storage_metadata.upsert("custom_key", "beta")
            self.assertEqual(storage.storage_metadata.get_value("custom_key"), "beta")

            metadata_keys = {record.key for record in storage.storage_metadata.list_all()}
            self.assertIn("custom_key", metadata_keys)

            storage.storage_metadata.delete("custom_key")
            self.assertIsNone(storage.storage_metadata.get_value("custom_key"))

    def test_recommendation_session_store_upsert_load_and_delete(self) -> None:
        user_id = UUID("11111111-1111-1111-1111-111111111111")
        session_id = UUID("22222222-2222-2222-2222-222222222222")
        other_session_id = UUID("33333333-3333-3333-3333-333333333333")

        with Storage(self.storage_configuration, embedding_model=self.embedding_model) as storage:
            first_message = RecommendationSessionMemoryRecord(
                user_id=user_id,
                session_id=session_id,
                chat_history_number=2,
                user_request="Suggest a beach vacation",
                system_response="Try Island Escape",
                query="beach holiday",
                recommendations=[
                    {
                        "code": "destination-1",
                        "score": 0.91,
                    },
                ],
                interest_preference={"beach": 1.0},
                logistical_preference={"max_cost_per_week": 900},
            )
            second_message = RecommendationSessionMemoryRecord(
                user_id=user_id,
                session_id=session_id,
                chat_history_number=1,
                user_request="I like hiking",
                system_response="Consider Alpine Peaks",
                query="mountain hiking",
                recommendations=[
                    {
                        "code": "destination-2",
                        "score": 0.88,
                    },
                ],
                interest_preference={"hiking": 1.0},
                logistical_preference={"months": ["jul", "aug"]},
            )

            storage.recommendation_sessions.upsert_many([first_message, second_message])

            loaded_messages = storage.recommendation_sessions.load_session(user_id, session_id)
            self.assertEqual([row.chat_history_number for row in loaded_messages], [1, 2])
            self.assertEqual(loaded_messages[0].recommendations[0]["code"], "destination-2")

            updated_message = RecommendationSessionMemoryRecord(
                user_id=user_id,
                session_id=session_id,
                chat_history_number=2,
                user_request="Suggest a beach vacation",
                system_response="Try Luxury Coast",
                query="luxury beach holiday",
                recommendations=[
                    {
                        "code": "destination-3",
                        "score": 0.95,
                    },
                ],
                interest_preference={"beach": 1.0, "luxury": 1.0},
                logistical_preference={"max_cost_per_week": 1500},
            )
            storage.recommendation_sessions.upsert_many([updated_message])

            reloaded_messages = storage.recommendation_sessions.load_session(user_id, session_id)
            self.assertEqual(reloaded_messages[1].system_response, "Try Luxury Coast")
            self.assertEqual(reloaded_messages[1].recommendations[0]["code"], "destination-3")

            other_session_message = RecommendationSessionMemoryRecord(
                user_id=user_id,
                session_id=other_session_id,
                chat_history_number=1,
                user_request="City break",
                system_response="Try Culture Capital",
                query="city museum",
                recommendations=[],
            )
            storage.recommendation_sessions.upsert_many([other_session_message])

            storage.recommendation_sessions.delete_session(user_id, session_id)

            self.assertEqual(storage.recommendation_sessions.load_session(user_id, session_id), [])
            self.assertEqual(len(storage.recommendation_sessions.load_session(user_id, other_session_id)), 1)


if __name__ == "__main__":
    unittest.main()
