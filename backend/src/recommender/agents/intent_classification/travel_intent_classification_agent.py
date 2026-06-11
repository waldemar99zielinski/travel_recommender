from __future__ import annotations

from typing import Literal

from pydantic import BaseModel
from pydantic import Field

from recommender.agents.base.base_agent import BaseAgent
from recommender.agents.base.base_agent import BaseAgentBuilder
from recommender.agents.intent_classification.travel_intent_classification_prompt import (
    travel_intent_classification_prompt_template,
)
from recommender.models.llm.llm import create_llm_chat_model
from recommender.models.llm.llm_config import LLMConfig


class TravelIntentClassificationInput(BaseModel):
    current_user_input: str = Field(..., description="Raw user input for the current turn")
    synthesized_query: str = Field(..., description="History-aware synthesized query for the current turn")


class TravelIntentClassificationResult(BaseModel):
    intent: Literal["recommendation", "conversation"] = Field(..., description="Selected travel intent")
    reason: str = Field(..., description="Short explanation of the chosen intent")


class TravelIntentClassificationAgentBuilder(BaseAgentBuilder):
    """Builder for TravelIntentClassificationAgent."""

    def __init__(self) -> None:
        super().__init__(TravelIntentClassificationAgent)

    def build(self) -> "TravelIntentClassificationAgent":
        llm = self._llm or create_llm_chat_model(LLMConfig())
        prompt = self._prompt or travel_intent_classification_prompt_template
        output_type = self._output_type or TravelIntentClassificationResult

        return TravelIntentClassificationAgent(
            llm=llm,
            prompt=prompt,
            output_type=output_type,
        )


class TravelIntentClassificationAgent(BaseAgent):
    """Classify in-scope travel messages into recommendation or conversation paths."""

    def invoke(
        self,
        input: TravelIntentClassificationInput,
    ) -> TravelIntentClassificationResult:
        prompt_inputs = self.prompt.format_messages(
            current_user_input=input.current_user_input,
            synthesized_query=input.synthesized_query,
        )
        return super().invoke(prompt_inputs)

    @classmethod
    def builder(cls) -> TravelIntentClassificationAgentBuilder:
        return TravelIntentClassificationAgentBuilder()
