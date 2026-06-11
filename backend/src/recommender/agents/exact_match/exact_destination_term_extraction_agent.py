from __future__ import annotations

from typing import Literal

from pydantic import BaseModel
from pydantic import Field

from recommender.agents.base.base_agent import BaseAgent
from recommender.agents.base.base_agent import BaseAgentBuilder
from recommender.agents.exact_match.exact_destination_term_extraction_prompt import (
    exact_destination_term_extraction_prompt_template,
)
from recommender.models.llm.llm import create_llm_chat_model
from recommender.models.llm.llm_config import LLMConfig


class ExactDestinationTermCandidate(BaseModel):
    """One extracted place-like term suitable for exact destination lookup."""

    phrase: str = Field(..., min_length=1, description="Extracted place or landmark phrase")
    entity_type: Literal["country", "region", "city", "landmark", "place", "unknown"] = Field(
        ..., description="Type of extracted place term"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the extracted candidate")


class ExactDestinationTermExtractionInput(BaseModel):
    """Input payload for exact destination term extraction."""

    current_user_input: str = Field(..., description="Raw user input for the current turn")
    synthesized_query: str = Field(..., description="History-aware synthesized query for the current turn")


class ExactDestinationTermExtractionResult(BaseModel):
    """Structured output containing candidate place terms for exact lookup."""

    candidates: list[ExactDestinationTermCandidate] = Field(
        default_factory=list,
        description="Candidate exact place terms extracted from the request",
    )


class ExactDestinationTermExtractionAgentBuilder(BaseAgentBuilder):
    """Builder for ExactDestinationTermExtractionAgent."""

    def __init__(self) -> None:
        super().__init__(ExactDestinationTermExtractionAgent)

    def build(self) -> "ExactDestinationTermExtractionAgent":
        llm = self._llm or create_llm_chat_model(LLMConfig())
        prompt = self._prompt or exact_destination_term_extraction_prompt_template
        output_type = self._output_type or ExactDestinationTermExtractionResult

        return ExactDestinationTermExtractionAgent(
            llm=llm,
            prompt=prompt,
            output_type=output_type,
        )


class ExactDestinationTermExtractionAgent(BaseAgent):
    """Extract explicit place terms that should trigger exact destination search."""

    def invoke(
        self,
        input: ExactDestinationTermExtractionInput,
    ) -> ExactDestinationTermExtractionResult:
        prompt_inputs = self.prompt.format_messages(
            current_user_input=input.current_user_input,
            synthesized_query=input.synthesized_query,
        )
        result = super().invoke(prompt_inputs)

        normalized_candidates: list[ExactDestinationTermCandidate] = []
        seen_phrases: set[str] = set()
        for candidate in result.candidates:
            phrase = candidate.phrase.strip()
            normalized_phrase = phrase.lower()
            if not phrase or normalized_phrase in seen_phrases:
                continue
            seen_phrases.add(normalized_phrase)
            normalized_candidates.append(
                ExactDestinationTermCandidate(
                    phrase=phrase,
                    entity_type=candidate.entity_type,
                    confidence=float(candidate.confidence),
                )
            )

        return ExactDestinationTermExtractionResult(candidates=normalized_candidates[:3])

    @classmethod
    def builder(cls) -> ExactDestinationTermExtractionAgentBuilder:
        return ExactDestinationTermExtractionAgentBuilder()
