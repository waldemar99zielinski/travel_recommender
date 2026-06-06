from __future__ import annotations

from langchain_core.language_models import BaseChatModel

from recommender.graphs.recommendation_v2.agents.response_generation.need_more_information.models import (
    RecommendationV2NeedMoreInformationResponseGenerationInput,
)
from recommender.graphs.recommendation_v2.agents.response_generation.need_more_information.prompt import (
    prompt,
)
from recommender.graphs.recommendation_v2.agents.response_generation.response_generation_result import (
    RecommendationV2ResponseGenerationResult,
)
from recommender.graphs.recommendation_v2.models import serialize_chat_history
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class RecommendationV2NeedMoreInformationResponseGenerationAgent:
    """Agent that generates a response asking the user for more recommendation details."""

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
        inputs: RecommendationV2NeedMoreInformationResponseGenerationInput,
    ) -> RecommendationV2ResponseGenerationResult:
        prompt_value = self._prompt_template.format_prompt(
            current_user_request=inputs.current_user_request,
            chat_history=serialize_chat_history(inputs.chat_history),
        )
        result = self._structured_output_llm.invoke(prompt_value.to_messages())
        logger.verbose("Raw need-more-information response-generation result: %s", result)
        output = RecommendationV2ResponseGenerationResult.model_validate(result)

        return output
