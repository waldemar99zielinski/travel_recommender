from __future__ import annotations

from langchain_core.language_models import BaseChatModel

from recommender.graphs.recommendation_v2.agents.response_generation.no_results_for_recommendation.models import (
    RecommendationV2NoResultsForRecommendationResponseGenerationInput,
)
from recommender.graphs.recommendation_v2.agents.response_generation.no_results_for_recommendation.prompt import (
    prompt,
)
from recommender.graphs.recommendation_v2.agents.response_generation.response_generation_result import (
    RecommendationV2ResponseGenerationResult,
)
from recommender.graphs.recommendation_v2.filter_models import (
    serialize_travel_destination_filter,
)
from recommender.graphs.recommendation_v2.models import serialize_chat_history
from recommender.graphs.recommendation_v2.models import serialize_recommendations
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class RecommendationV2NoResultsForRecommendationResponseGenerationAgent:
    """Agent that generates a response for recommendation_v2 runs with no final results."""

    def __init__(
        self,
        *,
        llm: BaseChatModel,
    ) -> None:
        self._llm = llm
        self._prompt_template = prompt
        self._structured_output_llm = self._llm.with_structured_output(
            RecommendationV2ResponseGenerationResult,
        )

    def invoke(
        self,
        inputs: RecommendationV2NoResultsForRecommendationResponseGenerationInput,
    ) -> RecommendationV2ResponseGenerationResult:
        prompt_value = self._prompt_template.format_prompt(
            current_user_request=inputs.current_user_request,
            synthesized_user_request=inputs.synthesized_user_request or "None",
            travel_destination_filter=serialize_travel_destination_filter(
                inputs.travel_destination_filter,
            ),
            recommendations=serialize_recommendations(inputs.recommendations),
            final_recommendations=serialize_recommendations(inputs.final_recommendations),
            chat_history=serialize_chat_history(inputs.chat_history),
        )
        result = self._structured_output_llm.invoke(prompt_value.to_messages())
        logger.verbose("Raw no-results response-generation result: %s", result)
        output = RecommendationV2ResponseGenerationResult.model_validate(result)

        return output
