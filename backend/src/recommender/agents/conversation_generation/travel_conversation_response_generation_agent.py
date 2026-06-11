from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field

from recommender.agents.base.base_agent import BaseAgent
from recommender.agents.base.base_agent import BaseAgentBuilder
from recommender.agents.conversation_generation.travel_conversation_response_generation_prompt import (
    travel_conversation_response_generation_prompt_template,
)
from recommender.models.llm.llm import create_llm_chat_model
from recommender.models.llm.llm_config import LLMConfig
from storage.stores.search_models import ScoredTravelDestination


class TravelConversationResponseGenerationInput(BaseModel):
    user_input: str = Field(..., description="Current raw user input")
    synthesized_query: str = Field(..., description="History-aware query for the current turn")
    history_summary: str = Field(..., description="Short formatted summary of recent session history")
    destination_context_summary: str = Field(..., description="Summary of retrieved destination context")


class TravelConversationResponseGenerationResult(BaseModel):
    message: str = Field(..., description="Grounded conversational answer for the user")


class TravelConversationResponseGenerationAgentBuilder(BaseAgentBuilder):
    """Builder for TravelConversationResponseGenerationAgent."""

    def __init__(self) -> None:
        super().__init__(TravelConversationResponseGenerationAgent)

    def build(self) -> "TravelConversationResponseGenerationAgent":
        llm = self._llm or create_llm_chat_model(LLMConfig())
        prompt = self._prompt or travel_conversation_response_generation_prompt_template
        output_type = self._output_type or TravelConversationResponseGenerationResult

        return TravelConversationResponseGenerationAgent(
            llm=llm,
            prompt=prompt,
            output_type=output_type,
        )


class TravelConversationResponseGenerationAgent(BaseAgent):
    """Generate a grounded conversational answer for an in-scope travel follow-up."""

    def invoke(
        self,
        input: TravelConversationResponseGenerationInput,
    ) -> TravelConversationResponseGenerationResult:
        prompt_inputs = self.prompt.format_messages(
            user_input=input.user_input,
            synthesized_query=input.synthesized_query,
            history_summary=input.history_summary,
            destination_context_summary=input.destination_context_summary,
        )
        return super().invoke(prompt_inputs)

    @staticmethod
    def summarize_destinations(recommendations: list[ScoredTravelDestination]) -> str:
        if not recommendations:
            return "None"

        parts: list[str] = []
        for item in recommendations[:3]:
            destination = item.destination
            parts.append(
                f"{destination.region}: popularity={destination.popularity}, cost_per_week={destination.cost_per_week}, "
                f"description={destination.description}"
            )
        return " | ".join(parts)

    @classmethod
    def builder(cls) -> TravelConversationResponseGenerationAgentBuilder:
        return TravelConversationResponseGenerationAgentBuilder()
