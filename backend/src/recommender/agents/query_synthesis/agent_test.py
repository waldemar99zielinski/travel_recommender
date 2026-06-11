from __future__ import annotations

import unittest

from recommender.agents.query_synthesis.agent import (
    QuerySynthesisAgent,
)
from recommender.agents.query_synthesis.agent import (
    QuerySynthesisInput,
)
from recommender.agents.query_synthesis.agent import (
    QuerySynthesisResult,
)
from recommender.agents.query_synthesis.prompt import (
    prompt,
)


class _FakeStructuredRunnable:
    def __init__(self, response: QuerySynthesisResult) -> None:
        self._response = response

    def invoke(self, _inputs: object) -> QuerySynthesisResult:
        return self._response


class _FakeChatModel:
    def __init__(self, response: QuerySynthesisResult) -> None:
        self._response = response

    def with_structured_output(self, _output_type: object) -> _FakeStructuredRunnable:
        return _FakeStructuredRunnable(self._response)


class TestQuerySynthesisAgent(unittest.TestCase):
    def test_falls_back_to_current_request_when_model_returns_empty_query(self) -> None:
        agent = QuerySynthesisAgent(
            llm=_FakeChatModel(QuerySynthesisResult(synthesized_query="   ")),
            prompt=prompt,
            output_type=QuerySynthesisResult,
        )

        result = agent.invoke(
            QuerySynthesisInput(
                current_user_request="I want a quiet beach",
                previous_synthesized_query=None,
            )
        )

        self.assertEqual(result.synthesized_query, "I want a quiet beach")

    def test_falls_back_to_previous_and_current_request_when_both_exist(self) -> None:
        agent = QuerySynthesisAgent(
            llm=_FakeChatModel(QuerySynthesisResult(synthesized_query="")),
            prompt=prompt,
            output_type=QuerySynthesisResult,
        )

        result = agent.invoke(
            QuerySynthesisInput(
                current_user_request="same but cheaper",
                previous_synthesized_query="quiet beach destination in Spain",
            )
        )

        self.assertEqual(
            result.synthesized_query,
            "quiet beach destination in Spain same but cheaper",
        )


if __name__ == "__main__":
    unittest.main()
