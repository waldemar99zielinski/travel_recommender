import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from recommender.common.configuration import SqlStoreConfiguration
from recommender.models.data_flow.recommendation_session_history import RecommendationSessionHistory
from recommender.models.data_flow.user_preferences import Preference
from recommender.models.data_flow.user_preferences import PopularityPreference
from recommender.models.data_flow.user_preferences import PricePreference
from recommender.models.data_flow.user_preferences import TimeOfYearPreference
from recommender.models.data_flow.user_preferences import UserInterestPreferences
from recommender.models.data_flow.user_preferences import UserLogisticalPreferences
from recommender.store.sql.travel_destination_store import SqlStore


def _interest(index: int) -> UserInterestPreferences:
    return UserInterestPreferences(
        raw_user_query=f"interest query {index}",
        nature=Preference(strength=min(index + 1, 5), extracted_text=f"nature {index}"),
        hiking=Preference(strength=3, extracted_text=f"hiking {index}"),
        beach=Preference(strength=max(1, 5 - index), extracted_text=f"beach {index}"),
        watersports=Preference(strength=2, extracted_text=f"watersports {index}"),
        entertainment=Preference(strength=2, extracted_text=f"entertainment {index}"),
        wintersports=Preference(strength=1, extracted_text=f"wintersports {index}"),
        culture=Preference(strength=3, extracted_text=f"culture {index}"),
        culinary=Preference(strength=4, extracted_text=f"culinary {index}"),
        architecture=Preference(strength=2, extracted_text=f"architecture {index}"),
        shopping=Preference(strength=1, extracted_text=f"shopping {index}"),
    )


def _logistical(index: int) -> UserLogisticalPreferences:
    return UserLogisticalPreferences(
        raw_user_query=f"logistics query {index}",
        price=PricePreference(
            min_cost_per_week=100.0 * (index + 1),
            max_cost_per_week=500.0 * (index + 1),
            budget_tier=None,
            extracted_text=f"budget {index}",
        ),
        popularity=PopularityPreference(
            strength=min(index + 1, 5),
            extracted_text=f"popularity {index}",
        ),
        time_of_year=TimeOfYearPreference(
            months=["jun", "jul", "aug"] if index % 2 == 0 else ["jan", "feb", "dec"],
            season=None,
            extracted_text=f"season {index}",
        ),
    )


class TestRecommendationSessionMemorySaveLoad(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        db_file = Path(self.temp_dir.name) / "test_session.db"
        self.store = SqlStore(store_config=SqlStoreConfiguration(db_url=f"sqlite:///{db_file}"))
        self.store.load()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_save_and_load_empty_history(self) -> None:
        user_id = "test_user_123"
        session_id = "test_session_456"

        self.store.save_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
            history=RecommendationSessionHistory(),
        )

        loaded = self.store.load_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
        )

        self.assertEqual(loaded.query_by_chat_number, {})
        self.assertEqual(loaded.user_request_by_chat_number, {})
        self.assertEqual(loaded.system_response_by_chat_number, {})
        self.assertEqual(loaded.user_interest_preferences_by_chat_number, {})
        self.assertEqual(loaded.user_logistical_preferences_by_chat_number, {})
        self.assertEqual(loaded.query_history_list(), [])
        self.assertEqual(loaded.chat_history_list(), [])

    def test_save_and_load_single_turn(self) -> None:
        user_id = "test_user_single"
        session_id = "test_session_single"
        history = RecommendationSessionHistory(
            query_by_chat_number={0: "beach vacation"},
            user_request_by_chat_number={0: "I want a beach vacation"},
            system_response_by_chat_number={0: "Here are beach recommendations"},
            user_interest_preferences_by_chat_number={0: _interest(0)},
            user_logistical_preferences_by_chat_number={0: _logistical(0)},
        )

        self.store.save_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
            history=history,
        )

        loaded = self.store.load_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
        )

        self.assertEqual(loaded.query_by_chat_number[0], "beach vacation")
        self.assertEqual(loaded.user_request_by_chat_number[0], "I want a beach vacation")
        self.assertEqual(loaded.system_response_by_chat_number[0], "Here are beach recommendations")
        loaded_interest = loaded.user_interest_preferences_by_chat_number[0]
        loaded_logistical = loaded.user_logistical_preferences_by_chat_number[0]
        if loaded_interest.beach is None:
            self.fail("Expected beach preference to be present")
        if loaded_logistical.price is None:
            self.fail("Expected price preference to be present")
        self.assertEqual(loaded_interest.beach.strength, 5)
        self.assertEqual(loaded_logistical.price.max_cost_per_week, 500.0)
        self.assertEqual(loaded.query_history_list(), ["beach vacation"])
        self.assertEqual(
            loaded.chat_history_list(),
            ["I want a beach vacation", "Here are beach recommendations"],
        )

    def test_save_handles_duplicates_with_upsert(self) -> None:
        user_id = "test_user_upsert"
        session_id = "test_session_upsert"

        initial_history = RecommendationSessionHistory(
            query_by_chat_number={0: "beach"},
            user_request_by_chat_number={0: "beach please"},
            system_response_by_chat_number={0: "beach results"},
            user_interest_preferences_by_chat_number={0: _interest(0)},
            user_logistical_preferences_by_chat_number={0: _logistical(0)},
        )
        updated_history = RecommendationSessionHistory(
            query_by_chat_number={0: "beach updated", 1: "add hiking"},
            user_request_by_chat_number={0: "beach updated please", 1: "and hiking"},
            system_response_by_chat_number={0: "updated beach results", 1: "hiking options"},
            user_interest_preferences_by_chat_number={0: _interest(1), 1: _interest(2)},
            user_logistical_preferences_by_chat_number={0: _logistical(1), 1: _logistical(2)},
        )

        self.store.save_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
            history=initial_history,
        )
        self.store.save_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
            history=updated_history,
        )

        loaded = self.store.load_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
        )

        self.assertEqual(loaded.query_by_chat_number[0], "beach updated")
        self.assertEqual(loaded.query_by_chat_number[1], "add hiking")
        self.assertEqual(len(loaded.query_by_chat_number), 2)
        self.assertEqual(len(loaded.user_request_by_chat_number), 2)
        self.assertEqual(len(loaded.system_response_by_chat_number), 2)

    def test_load_non_existent_returns_empty_history(self) -> None:
        loaded = self.store.load_recommendation_session_history(
            user_id="non_existent_user",
            session_id="non_existent_session",
        )

        self.assertEqual(loaded.query_by_chat_number, {})
        self.assertEqual(loaded.chat_history_list(), [])

    def test_delete_removes_history(self) -> None:
        user_id = "test_user_delete"
        session_id = "test_session_delete"
        history = RecommendationSessionHistory(
            query_by_chat_number={0: "test query"},
            user_request_by_chat_number={0: "test request"},
            system_response_by_chat_number={0: "test response"},
            user_interest_preferences_by_chat_number={0: _interest(0)},
            user_logistical_preferences_by_chat_number={0: _logistical(0)},
        )

        self.store.save_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
            history=history,
        )

        self.store.delete_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
        )

        loaded_after_delete = self.store.load_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
        )
        self.assertEqual(loaded_after_delete.query_by_chat_number, {})

    def test_multiple_sessions_independent(self) -> None:
        user_id = "test_user_multi"
        session_id_1 = "test_session_1"
        session_id_2 = "test_session_2"

        history_1 = RecommendationSessionHistory(
            query_by_chat_number={0: "query1"},
            user_request_by_chat_number={0: "request1"},
            system_response_by_chat_number={0: "response1"},
        )
        history_2 = RecommendationSessionHistory(
            query_by_chat_number={0: "query2"},
            user_request_by_chat_number={0: "request2"},
            system_response_by_chat_number={0: "response2"},
        )

        self.store.save_recommendation_session_history(
            user_id=user_id,
            session_id=session_id_1,
            history=history_1,
        )
        self.store.save_recommendation_session_history(
            user_id=user_id,
            session_id=session_id_2,
            history=history_2,
        )

        loaded_1 = self.store.load_recommendation_session_history(
            user_id=user_id,
            session_id=session_id_1,
        )
        loaded_2 = self.store.load_recommendation_session_history(
            user_id=user_id,
            session_id=session_id_2,
        )

        self.assertEqual(loaded_1.query_by_chat_number[0], "query1")
        self.assertEqual(loaded_2.query_by_chat_number[0], "query2")

    def test_full_history_five_entries_two_views(self) -> None:
        user_id = "test_user_full"
        session_id = "test_session_full"

        query_by_chat_number: dict[int, str] = {}
        user_request_by_chat_number: dict[int, str] = {}
        system_response_by_chat_number: dict[int, str] = {}
        interest_by_chat_number: dict[int, UserInterestPreferences] = {}
        logistical_by_chat_number: dict[int, UserLogisticalPreferences] = {}

        for i in range(5):
            query_by_chat_number[i] = f"travel query {i}"
            user_request_by_chat_number[i] = f"user request {i}"
            system_response_by_chat_number[i] = f"system response {i}"
            interest_by_chat_number[i] = _interest(i)
            logistical_by_chat_number[i] = _logistical(i)

        history = RecommendationSessionHistory(
            query_by_chat_number=query_by_chat_number,
            user_request_by_chat_number=user_request_by_chat_number,
            system_response_by_chat_number=system_response_by_chat_number,
            user_interest_preferences_by_chat_number=interest_by_chat_number,
            user_logistical_preferences_by_chat_number=logistical_by_chat_number,
        )

        self.store.save_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
            history=history,
        )

        loaded = self.store.load_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
        )

        self.assertEqual(loaded.query_by_chat_number, query_by_chat_number)
        self.assertEqual(loaded.user_request_by_chat_number, user_request_by_chat_number)
        self.assertEqual(loaded.system_response_by_chat_number, system_response_by_chat_number)
        self.assertEqual(len(loaded.user_interest_preferences_by_chat_number), 5)
        self.assertEqual(len(loaded.user_logistical_preferences_by_chat_number), 5)

        self.assertEqual(
            loaded.query_history_list(),
            [f"travel query {i}" for i in range(5)],
        )
        self.assertEqual(
            loaded.chat_history_list(),
            [
                "user request 0",
                "system response 0",
                "user request 1",
                "system response 1",
                "user request 2",
                "system response 2",
                "user request 3",
                "system response 3",
                "user request 4",
                "system response 4",
            ],
        )


if __name__ == "__main__":
    unittest.main()
