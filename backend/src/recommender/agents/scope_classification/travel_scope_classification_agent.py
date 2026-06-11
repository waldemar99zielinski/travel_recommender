from __future__ import annotations

from typing import Literal

from pydantic import BaseModel
from pydantic import Field

from recommender.agents.base.base_agent import BaseAgent
from recommender.agents.base.base_agent import BaseAgentBuilder
from recommender.agents.scope_classification.travel_scope_classification_prompt import (
    travel_scope_classification_prompt_template,
)
from recommender.models.llm.llm import create_llm_chat_model
from recommender.models.llm.llm_config import LLMConfig


class TravelScopeClassificationInput(BaseModel):
    current_user_input: str = Field(..., description="Raw user input for the current turn")
    synthesized_query: str = Field(..., description="History-aware synthesized query for the current turn")


class TravelScopeClassificationResult(BaseModel):
    scope: Literal["in_scope", "out_of_scope"] = Field(..., description="Whether the request should be handled")
    reason: str = Field(..., description="Short explanation of the classification result")


class TravelScopeClassificationAgentBuilder(BaseAgentBuilder):
    """Builder for TravelScopeClassificationAgent."""

    def __init__(self) -> None:
        super().__init__(TravelScopeClassificationAgent)

    def build(self) -> "TravelScopeClassificationAgent":
        llm = self._llm or create_llm_chat_model(LLMConfig())
        prompt = self._prompt or travel_scope_classification_prompt_template
        output_type = self._output_type or TravelScopeClassificationResult

        return TravelScopeClassificationAgent(
            llm=llm,
            prompt=prompt,
            output_type=output_type,
        )


class TravelScopeClassificationAgent(BaseAgent):
    """Classify whether a chat turn belongs to the travel recommendation domain."""

    def invoke(
        self,
        input: TravelScopeClassificationInput,
    ) -> TravelScopeClassificationResult:
        prompt_inputs = self.prompt.format_messages(
            current_user_input=input.current_user_input,
            synthesized_query=input.synthesized_query,
        )
        return super().invoke(prompt_inputs)

    @classmethod
    def builder(cls) -> TravelScopeClassificationAgentBuilder:
        return TravelScopeClassificationAgentBuilder()
