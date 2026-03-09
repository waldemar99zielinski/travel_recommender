import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

from recommender.common.configuration import SqlStoreConfiguration
from recommender.models.data_flow.recommendation_session_history import RecommendationSessionHistory
from recommender.models.data_flow.user_preferences import (
    Preference,
    PricePreference,
    PopularityPreference,
    TimeOfYearPreference,
    UserInterestPreferences,
    UserLogisticalPreferences,
)
from recommender.store.sql.travel_destination_store import SqlStore
from recommender.store.sql.tables.recommendation_session_memory_table import (
    RecommendationSessionMemoryTable,
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
        history = RecommendationSessionHistory()
        
        self.store.save_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
            history=history,
        )
        
        loaded = self.store.load_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
        )
        
        self.assertEqual(loaded.query_history, [])
        self.assertEqual(loaded.chat_history, [])
        self.assertEqual(loaded.user_interest_preferences_history, [])
        self.assertEqual(loaded.user_logistical_preferences_history, [])

    def test_save_and_load_history_with_queries_and_chat(self) -> None:
        user_id = "test_user_123"
        session_id = "test_session_456"
        history = RecommendationSessionHistory(
            query_history=["beach vacation", "with hiking options"],
            chat_history=["I want a beach vacation", "Here are some beaches", "Add hiking options", "Here are hiking beaches"],
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
        
        self.assertEqual(loaded.query_history, history.query_history)
        self.assertEqual(loaded.chat_history, history.chat_history)

    def test_save_and_load_history_with_interest_preferences(self) -> None:
        user_id = "test_user_123"
        session_id = "test_session_456"
        interest_pref = UserInterestPreferences(
            raw_user_query="I love beaches and hiking",
            beach=Preference(strength=5, extracted_text="I love beaches"),
            hiking=Preference(strength=4, extracted_text="and hiking"),
        )
        history = RecommendationSessionHistory(
            query_history=["beach and hiking vacation"],
            chat_history=["I love beaches and hiking", "Great preferences!"],
            user_interest_preferences_history=[interest_pref],
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
        
        self.assertEqual(len(loaded.user_interest_preferences_history), 1)
        loaded_interest = loaded.user_interest_preferences_history[0]
        self.assertEqual(loaded_interest.beach.strength, 5)
        self.assertEqual(loaded_interest.hiking.strength, 4)

    def test_save_and_load_history_with_logistical_preferences(self) -> None:
        user_id = "test_user_123"
        session_id = "test_session_456"
        logistical_pref = UserLogisticalPreferences(
            raw_user_query="under 1000 euros",
            price=PricePreference(
                max_cost_per_week=1000.0,
                min_cost_per_week=None,
                budget_tier=None,
                extracted_text="under 1000 euros",
            ),
            popularity=PopularityPreference(
                strength=3,
                extracted_text="moderate popularity",
            ),
            time_of_year=TimeOfYearPreference(
                months=["jun", "jul", "aug"],
                season=None,
                extracted_text="summer months",
            ),
        )
        history = RecommendationSessionHistory(
            query_history=["vacation under 1000"],
            chat_history=["under 1000 euros", "Here are options"],
            user_logistical_preferences_history=[logistical_pref],
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
        
        self.assertEqual(len(loaded.user_logistical_preferences_history), 1)
        loaded_logistical = loaded.user_logistical_preferences_history[0]
        self.assertEqual(loaded_logistical.price.max_cost_per_week, 1000.0)
        self.assertEqual(loaded_logistical.popularity.strength, 3)
        self.assertEqual(loaded_logistical.time_of_year.months, ["jun", "jul", "aug"])

    def test_save_handles_duplicates(self) -> None:
        user_id = "test_user_123"
        session_id = "test_session_456"
        interest_pref1 = UserInterestPreferences(
            raw_user_query="beach",
            beach=Preference(strength=5, extracted_text="beach"),
        )
        interest_pref2 = UserInterestPreferences(
            raw_user_query="hiking",
            hiking=Preference(strength=4, extracted_text="hiking"),
        )
        
        history1 = RecommendationSessionHistory(
            query_history=["beach vacation"],
            chat_history=["I want beach", "Here are beaches"],
            user_interest_preferences_history=[interest_pref1],
        )
        history2 = RecommendationSessionHistory(
            query_history=["beach vacation", "add hiking"],
            chat_history=["I want beach", "Here are beaches", "add hiking", "Here are hiking beaches"],
            user_interest_preferences_history=[interest_pref1, interest_pref2],
        )
        
        self.store.save_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
            history=history1,
        )
        
        self.store.save_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
            history=history2,
        )
        
        loaded = self.store.load_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
        )
        
        self.assertEqual(len(loaded.query_history), 2)
        self.assertEqual(len(loaded.chat_history), 4)
        self.assertEqual(len(loaded.user_interest_preferences_history), 2)

    def test_load_non_existent_returns_empty_history(self) -> None:
        loaded = self.store.load_recommendation_session_history(
            user_id="non_existent_user",
            session_id="non_existent_session",
        )
        
        self.assertEqual(loaded.query_history, [])
        self.assertEqual(loaded.chat_history, [])

    def test_delete_removes_history(self) -> None:
        user_id = "test_user_123"
        session_id = "test_session_456"
        history = RecommendationSessionHistory(
            query_history=["test query"],
            chat_history=["test request", "test response"],
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
        self.assertEqual(len(loaded.query_history), 1)
        
        self.store.delete_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
        )
        
        loaded_after_delete = self.store.load_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
        )
        self.assertEqual(len(loaded_after_delete.query_history), 0)

    def test_multiple_sessions_independent(self) -> None:
        user_id = "test_user_123"
        session_id = "test_session_456"
        session_id_2 = "test_session_789"
        
        history1 = RecommendationSessionHistory(
            query_history=["query1"],
            chat_history=["request1", "response1"],
        )
        history2 = RecommendationSessionHistory(
            query_history=["query2"],
            chat_history=["request2", "response2"],
        )
        
        self.store.save_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
            history=history1,
        )
        self.store.save_recommendation_session_history(
            user_id=user_id,
            session_id=session_id_2,
            history=history2,
        )
        
        loaded1 = self.store.load_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
        )
        loaded2 = self.store.load_recommendation_session_history(
            user_id=user_id,
            session_id=session_id_2,
        )
        
        self.assertEqual(loaded1.query_history, ["query1"])
        self.assertEqual(loaded2.query_history, ["query2"])

    def test_save_and_load_full_history_five_entries(self) -> None:
        user_id = "test_user_full"
        session_id = "test_session_full"
        
        entries = []
        for i in range(5):
            interest_pref = UserInterestPreferences(
                raw_user_query=f"query {i}",
                nature=Preference(strength=i+1, extracted_text=f"nature {i}"),
                beach=Preference(strength=5-i, extracted_text=f"beach {i}"),
                hiking=Preference(strength=3, extracted_text=f"hiking {i}"),
                watersports=Preference(strength=4, extracted_text=f"watersports {i}"),
                entertainment=Preference(strength=2, extracted_text=f"entertainment {i}"),
                wintersports=Preference(strength=1, extracted_text=f"wintersports {i}"),
                culture=Preference(strength=3, extracted_text=f"culture {i}"),
                culinary=Preference(strength=4, extracted_text=f"culinary {i}"),
                architecture=Preference(strength=2, extracted_text=f"architecture {i}"),
                shopping=Preference(strength=1, extracted_text=f"shopping {i}"),
            )
            
            logistical_pref = UserLogisticalPreferences(
                raw_user_query=f"query {i}",
                price=PricePreference(
                    min_cost_per_week=100.0 * (i + 1),
                    max_cost_per_week=500.0 * (i + 1),
                    budget_tier=None,
                    extracted_text=f"budget {i}",
                ),
                popularity=PopularityPreference(
                    strength=i + 1,
                    extracted_text=f"popularity {i}",
                ),
                time_of_year=TimeOfYearPreference(
                    months=["jan", "feb", "dec"] if i % 2 == 0 else ["jun", "jul", "aug"],
                    season=None,
                    extracted_text=f"season {i}",
                ),
            )
            
            entries.append((interest_pref, logistical_pref))
        
        query_history = [f"travel destination {i}" for i in range(5)]
        chat_history = []
        interest_history = []
        logistical_history = []
        
        for i in range(5):
            chat_history.append(f"User request {i}")
            chat_history.append(f"System response {i}")
            interest_history.append(entries[i][0])
            logistical_history.append(entries[i][1])
        
        history = RecommendationSessionHistory(
            query_history=query_history,
            chat_history=chat_history,
            user_interest_preferences_history=interest_history,
            user_logistical_preferences_history=logistical_history,
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
        
        self.assertEqual(len(loaded.query_history), 5)
        self.assertEqual(len(loaded.chat_history), 10)
        self.assertEqual(len(loaded.user_interest_preferences_history), 5)
        self.assertEqual(len(loaded.user_logistical_preferences_history), 5)
        
        for i in range(5):
            self.assertEqual(loaded.query_history[i], query_history[i])
            self.assertEqual(loaded.chat_history[i * 2], f"User request {i}")
            self.assertEqual(loaded.chat_history[i * 2 + 1], f"System response {i}")
        
        for i in range(5):
            loaded_interest = loaded.user_interest_preferences_history[i]
            self.assertEqual(loaded_interest.nature.strength, i + 1)
            self.assertEqual(loaded_interest.beach.strength, 5 - i)
            self.assertEqual(loaded_interest.hiking.strength, 3)
            self.assertEqual(loaded_interest.watersports.strength, 4)
            self.assertEqual(loaded_interest.entertainment.strength, 2)
            self.assertEqual(loaded_interest.wintersports.strength, 1)
            self.assertEqual(loaded_interest.culture.strength, 3)
            self.assertEqual(loaded_interest.culinary.strength, 4)
            self.assertEqual(loaded_interest.architecture.strength, 2)
            self.assertEqual(loaded_interest.shopping.strength, 1)
        
        for i in range(5):
            loaded_logistical = loaded.user_logistical_preferences_history[i]
            self.assertEqual(loaded_logistical.price.min_cost_per_week, 100.0 * (i + 1))
            self.assertEqual(loaded_logistical.price.max_cost_per_week, 500.0 * (i + 1))
            self.assertEqual(loaded_logistical.popularity.strength, i + 1)
            expected_months = ["jan", "feb", "dec"] if i % 2 == 0 else ["jun", "jul", "aug"]
            self.assertEqual(loaded_logistical.time_of_year.months, expected_months)
        
        self.assertEqual(loaded.query_history, query_history)
        self.assertEqual(loaded.chat_history, chat_history)

    def test_save_and_load_full_history_two_ways(self) -> None:
        user_id = "test_user_two_ways"
        session_id = "test_session_two_ways"
        
        interest_pref = UserInterestPreferences(
            raw_user_query="beach vacation",
            beach=Preference(strength=5, extracted_text="beach"),
            hiking=Preference(strength=3, extracted_text="hiking"),
            culture=Preference(strength=2, extracted_text="culture"),
        )
        
        logistical_pref = UserLogisticalPreferences(
            raw_user_query="budget trip",
            price=PricePreference(
                min_cost_per_week=500.0,
                max_cost_per_week=1500.0,
                budget_tier=None,
                extracted_text="budget",
            ),
            popularity=PopularityPreference(
                strength=4,
                extracted_text="popular",
            ),
            time_of_year=TimeOfYearPreference(
                months=["jun", "jul", "aug"],
                season=None,
                extracted_text="summer",
            ),
        )
        
        history = RecommendationSessionHistory(
            query_history=["beach destination", "budget options"],
            chat_history=[
                "I want a beach vacation", "Here are beaches",
                "under 1500 budget", "Here are budget options"
            ],
            user_interest_preferences_history=[interest_pref, interest_pref],
            user_logistical_preferences_history=[logistical_pref, logistical_pref],
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
        
        self.assertEqual(loaded.query_history, ["beach destination", "budget options"])
        self.assertEqual(len(loaded.chat_history), 4)
        self.assertEqual(len(loaded.user_interest_preferences_history), 2)
        self.assertEqual(len(loaded.user_logistical_preferences_history), 2)
        
        self.assertEqual(loaded.user_interest_preferences_history[0].beach.strength, 5)
        self.assertEqual(loaded.user_interest_preferences_history[1].beach.strength, 5)
        self.assertEqual(loaded.user_logistical_preferences_history[0].price.max_cost_per_week, 1500.0)
        self.assertEqual(loaded.user_logistical_preferences_history[1].price.max_cost_per_week, 1500.0)
        
        history_updated = RecommendationSessionHistory(
            query_history=["beach destination", "budget options", "add hiking"],
            chat_history=[
                "I want a beach vacation", "Here are beaches",
                "under 1500 budget", "Here are budget options",
                "add hiking", "Here are hiking options"
            ],
            user_interest_preferences_history=[interest_pref, interest_pref, interest_pref],
            user_logistical_preferences_history=[logistical_pref, logistical_pref, logistical_pref],
        )
        
        self.store.save_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
            history=history_updated,
        )
        
        loaded_after_update = self.store.load_recommendation_session_history(
            user_id=user_id,
            session_id=session_id,
        )
        
        self.assertEqual(len(loaded_after_update.query_history), 3)
        self.assertEqual(len(loaded_after_update.chat_history), 6)
        self.assertEqual(len(loaded_after_update.user_interest_preferences_history), 3)
        self.assertEqual(len(loaded_after_update.user_logistical_preferences_history), 3)


if __name__ == "__main__":
    unittest.main()
