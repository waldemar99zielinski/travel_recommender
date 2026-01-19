from __future__ import annotations

from recommender.agents.base.base_agent import BaseAgent, BaseAgentBuilder
from recommender.models.data_flow.user_preferences import UserPreferences
from recommender.models.llm.llm import create_llm_chat_model
from recommender.models.llm.llm_config import LLMConfig
from recommender.agents.preference_extraction.preference_extraction_prompt import prompt_tempalate


class PreferenceExtractionAgentBuilder(BaseAgentBuilder):
    """
    Builder for PreferenceExtractionAgent.
    """

    def __init__(self):
        super().__init__('PreferenceExtractionAgentBuilder')

    def build(self) -> 'PreferenceExtractionAgent':
        """
        Implementation of the abstract build method.
        Applies defaults specific to Preference Extraction.
        """
        llm = self._llm or create_llm_chat_model(LLMConfig())

        if not self._prompt:
            self._prompt = prompt_tempalate

        if not self._output_type:
            self._output_type = UserPreferences

        return PreferenceExtractionAgent(
            llm=llm,
            prompt=self._prompt,
            output_type=self._output_type
        )

class PreferenceExtractionAgent(BaseAgent):
    """
    Agent to extract user category preferences from chat transcripts.
    Uses a structured output Pydantic model for UserPreferenceEvaluation.
    """

    def invoke(self, user_query: str) -> UserPreferences:
        input = self.prompt.format_messages(raw_user_query=user_query)
        return super().invoke(input)

    @classmethod
    def builder(cls) -> PreferenceExtractionAgentBuilder:
        return PreferenceExtractionAgentBuilder()
