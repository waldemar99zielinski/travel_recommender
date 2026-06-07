from __future__ import annotations

from langchain_core.language_models import BaseChatModel

from recommender.graphs.recommendation_v2.agents.query_keyword_extraction.models import (
    RecommendationV2QueryKeywordExtractionInput,
)
from recommender.graphs.recommendation_v2.agents.query_keyword_extraction.models import (
    RecommendationV2QueryKeywordExtractionResult,
)
from recommender.graphs.recommendation_v2.agents.query_keyword_extraction.prompt import (
    prompt,
)


class RecommendationV2QueryKeywordExtractionAgent:
    """Agent that extracts concrete direct-search keywords from a synthesized query."""

    def __init__(
        self,
        *,
        llm: BaseChatModel,
    ) -> None:
        self._llm = llm
        self._prompt_template = prompt
        self._structured_output_llm = self._llm.with_structured_output(
            RecommendationV2QueryKeywordExtractionResult,
        )

    def invoke(
        self,
        inputs: RecommendationV2QueryKeywordExtractionInput,
    ) -> RecommendationV2QueryKeywordExtractionResult:
        prompt_value = self._prompt_template.format_prompt(
            synthesized_query=inputs.synthesized_query,
        )
        result = self._structured_output_llm.invoke(prompt_value.to_messages())
        output = RecommendationV2QueryKeywordExtractionResult.model_validate(result)

        normalized_keywords: list[str] = []
        seen_keywords: set[str] = set()
        for keyword in output.keywords:
            normalized_keyword = keyword.strip()
            if not normalized_keyword:
                continue

            keyword_key = normalized_keyword.casefold()
            if keyword_key in seen_keywords:
                continue

            seen_keywords.add(keyword_key)
            normalized_keywords.append(normalized_keyword)

        return output.model_copy(update={"keywords": normalized_keywords})
