from __future__ import annotations

from recommender.agents.base.base_agent import BaseAgent, BaseAgentBuilder
from recommender.models.data_flow.user_preferences import UserInterestPreferences
from recommender.models.llm.llm import create_llm_chat_model
from recommender.models.llm.llm_config import LLMConfig
from recommender.agents.preference_extraction.user_interest_preference_extraction_prompt import user_interest_preference_extraction_prompt_template


class UserInterestPreferenceExtractionAgentBuilder(BaseAgentBuilder):
    """
    Builder for UserInterestPreferenceExtractionAgent.
    """

    def __init__(self):
        super().__init__('UserInterestPreferenceExtractionAgentBuilder')

    def build(self) -> 'UserInterestPreferenceExtractionAgent':
        """
        Implementation of the abstract build method.
        Applies defaults specific to Preference Extraction.
        """
        llm = self._llm or create_llm_chat_model(LLMConfig())

        if not self._prompt:
            self._prompt = user_interest_preference_extraction_prompt_template

        if not self._output_type:
            self._output_type = UserInterestPreferences

        return UserInterestPreferenceExtractionAgent(
            llm=llm,
            prompt=self._prompt,
            output_type=self._output_type
        )

class UserInterestPreferenceExtractionAgent(BaseAgent):
    """
    Agent to extract user category preferences from chat transcripts.
    Uses a structured output Pydantic model for UserPreferenceEvaluation.
    """

    def invoke(self, user_query: str) -> UserInterestPreferences:
        input = self.prompt.format_messages(raw_user_query=user_query)
        return super().invoke(input)

    @classmethod
    def builder(cls) -> UserInterestPreferenceExtractionAgentBuilder:
        return UserInterestPreferenceExtractionAgentBuilder()
