from __future__ import annotations

from recommender.agents.base.base_agent import BaseAgent
from recommender.agents.base.base_agent import BaseAgentBuilder
from recommender.agents.preference_extraction.user_logistical_preference_extraction_prompt import (
    user_logistical_preference_extraction_prompt_template,
)
from recommender.models.data_flow.user_preferences import UserLogisticalPreferences
from recommender.models.llm.llm import create_llm_chat_model
from recommender.models.llm.llm_config import LLMConfig


class UserLogisticalPreferenceExtractionAgentBuilder(BaseAgentBuilder):
    """Builder for UserLogisticalPreferenceExtractionAgent."""

    def __init__(self):
        super().__init__(UserLogisticalPreferenceExtractionAgent)

    def build(self) -> "UserLogisticalPreferenceExtractionAgent":
        llm = self._llm or create_llm_chat_model(LLMConfig())

        if not self._prompt:
            self._prompt = user_logistical_preference_extraction_prompt_template

        if not self._output_type:
            self._output_type = UserLogisticalPreferences

        return UserLogisticalPreferenceExtractionAgent(
            llm=llm,
            prompt=self._prompt,
            output_type=self._output_type,
        )


class UserLogisticalPreferenceExtractionAgent(BaseAgent):
    """Agent to extract user logistical preferences from raw user query."""

    def invoke(self, user_query: str) -> UserLogisticalPreferences:
        inputs = self.prompt.format_messages(raw_user_query=user_query)
        return super().invoke(inputs)

    @classmethod
    def builder(cls) -> UserLogisticalPreferenceExtractionAgentBuilder:
        return UserLogisticalPreferenceExtractionAgentBuilder()
