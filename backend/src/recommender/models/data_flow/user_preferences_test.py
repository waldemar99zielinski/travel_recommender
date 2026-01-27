import unittest

from src.recommender.models.data_flow.user_preferences import UserPreferences

class TestUserPreferencesModel(unittest.TestCase):
    def test_preference_presence_detection(self):
        prefs = UserPreferences(
            raw_user_query="I like to travel."
        )
        self.assertFalse(prefs.are_preferences_present())

    def test_are_preferences_present_one(self):
        from src.recommender.models.data_flow.user_preferences import Preference
        prefs = UserPreferences(
            raw_user_query="I like hiking.",
            hiking=Preference(strength=5, extracted_text="hiking")
        )
        self.assertTrue(prefs.are_preferences_present())

    def test_are_preferences_present_multiple(self):
        from src.recommender.models.data_flow.user_preferences import Preference
        prefs = UserPreferences(
            raw_user_query="I like hiking and nature.",
            hiking=Preference(strength=4, extracted_text="hiking"),
            nature=Preference(strength=3, extracted_text="nature")
        )
        self.assertTrue(prefs.are_preferences_present())

    def test_are_preferences_present_all_none(self):
        prefs = UserPreferences(
            raw_user_query="No preferences."
        )
        self.assertFalse(prefs.are_preferences_present())


if __name__ == "__main__":
    unittest.main()
