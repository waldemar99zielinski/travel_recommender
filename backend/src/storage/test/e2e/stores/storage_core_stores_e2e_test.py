from __future__ import annotations

import sys
import unittest
from pathlib import Path
from uuid import UUID

sys.path.append(str(Path(__file__).resolve().parents[4]))

from storage.configuration import MigrationConfiguration
from storage.configuration import StorageConfiguration
from storage.configuration import StorageEngineConfiguration
from storage.models.chat_record import ChatRecord
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

    def test_chat_store_upsert_load_and_delete(self) -> None:
        user_id = UUID("11111111-1111-1111-1111-111111111111")
        session_id = UUID("22222222-2222-2222-2222-222222222222")
        other_session_id = UUID("33333333-3333-3333-3333-333333333333")

        with Storage(self.storage_configuration, embedding_model=self.embedding_model) as storage:
            first_message = ChatRecord(
                user_id=user_id,
                session_id=session_id,
                chat_history_number=2,
                user_request="Suggest a beach vacation",
                system_response="Try Island Escape",
                synthesized_query="beach holiday",
                travel_destination_filter={
                    "regions": [
                        {
                            "field_name": "parent_region",
                            "region_name": "Caribbean",
                            "type": "include",
                        }
                    ],
                    "budget": {
                        "max_cost_per_week": 700,
                    },
                    "seasonality": {
                        "season": "winter",
                        "months": ["dec", "jan", "feb"],
                    },
                },
                recommendations=[
                    {
                        "code": "destination-1",
                        "score": 0.91,
                    },
                ],
            )
            second_message = ChatRecord(
                user_id=user_id,
                session_id=session_id,
                chat_history_number=1,
                user_request="I like hiking",
                system_response="Consider Alpine Peaks",
                synthesized_query="mountain hiking",
                recommendations=[
                    {
                        "code": "destination-2",
                        "score": 0.88,
                    },
                ],
            )

            storage.chat.upsert_many([first_message, second_message])

            loaded_messages = storage.chat.load_session(user_id, session_id)
            self.assertEqual([row.chat_history_number for row in loaded_messages], [1, 2])
            self.assertEqual(loaded_messages[0].recommendations[0]["code"], "destination-2")
            self.assertEqual(
                loaded_messages[1].travel_destination_filter["regions"][0]["region_name"],
                "Caribbean",
            )
            self.assertEqual(
                loaded_messages[1].travel_destination_filter["budget"]["max_cost_per_week"],
                700,
            )
            self.assertEqual(
                loaded_messages[1].travel_destination_filter["seasonality"]["season"],
                "winter",
            )

            updated_message = ChatRecord(
                user_id=user_id,
                session_id=session_id,
                chat_history_number=2,
                user_request="Suggest a beach vacation",
                system_response="Try Luxury Coast",
                synthesized_query="luxury beach holiday",
                recommendations=[
                    {
                        "code": "destination-3",
                        "score": 0.95,
                    },
                ],
            )
            storage.chat.upsert_many([updated_message])

            reloaded_messages = storage.chat.load_session(user_id, session_id)
            self.assertEqual(reloaded_messages[1].system_response, "Try Luxury Coast")
            self.assertEqual(reloaded_messages[1].recommendations[0]["code"], "destination-3")

            other_session_message = ChatRecord(
                user_id=user_id,
                session_id=other_session_id,
                chat_history_number=1,
                user_request="City break",
                system_response="Try Culture Capital",
                synthesized_query="city museum",
                recommendations=[],
            )
            storage.chat.upsert_many([other_session_message])

            storage.chat.delete_session(user_id, session_id)

            self.assertEqual(storage.chat.load_session(user_id, session_id), [])
            self.assertEqual(len(storage.chat.load_session(user_id, other_session_id)), 1)


if __name__ == "__main__":
    unittest.main()
