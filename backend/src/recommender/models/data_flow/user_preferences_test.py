import unittest

from recommender.models.data_flow.user_preferences import (
    Preference,
    PricePreference,
    UserInterestPreferences,
    UserLogisticalPreferences,
)

class TestUserPreferencesModel(unittest.TestCase):
    def test_preference_presence_detection(self):
        prefs = UserInterestPreferences(
            raw_user_query="I like to travel.",
        )
        self.assertFalse(prefs.are_preferences_present())

    def test_are_preferences_present_one(self):
        prefs = UserInterestPreferences(
            raw_user_query="I like hiking.",
            hiking=Preference(strength=5, extracted_text="hiking"),
        )
        self.assertTrue(prefs.are_preferences_present())

    def test_are_preferences_present_multiple(self):
        prefs = UserInterestPreferences(
            raw_user_query="I like hiking and nature.",
            nature=Preference(strength=3, extracted_text="nature"),
            hiking=Preference(strength=4, extracted_text="hiking"),
        )
        self.assertTrue(prefs.are_preferences_present())

    def test_are_preferences_present_all_none(self):
        prefs = UserInterestPreferences(
            raw_user_query="No preferences.",
        )
        self.assertFalse(prefs.are_preferences_present())

    def test_are_preferences_present_price_preference(self):
        prefs = UserLogisticalPreferences(
            raw_user_query="I need a trip under 500 per week.",
            price=PricePreference(
                min_cost_per_week=200,
                max_cost_per_week=500,
                budget_tier="low",
                budget_range_label="budget",
                extracted_text="under 500 per week",
            ),
            popularity=None,
            time_of_year=None,
        )
        self.assertTrue(prefs.are_preferences_present())


if __name__ == "__main__":
    unittest.main()
