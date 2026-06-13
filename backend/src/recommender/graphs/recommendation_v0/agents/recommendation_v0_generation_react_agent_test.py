from __future__ import annotations

import unittest
from unittest import mock
from uuid import UUID

from recommender.graphs.recommendation_v0.agents import recommendation_v0_generation_react_agent as module
from recommender.graphs.recommendation_v0.agents.recommendation_v0_generation_models import AgentOutput
from recommender.graphs.recommendation_v0.models import RecommendationV0
from storage.models.chat_record import ChatRecord


class _FakeRunnable:
    def __init__(self, result: object) -> None:
        self._result = result
        self.invocations: list[object] = []

    def invoke(self, inputs: object) -> object:
        self.invocations.append(inputs)
        return self._result


class _FakeChatModel:
    def __init__(self, structured_result: AgentOutput) -> None:
        self._structured_result = structured_result

    def with_structured_output(self, _output_type: object) -> _FakeRunnable:
        return _FakeRunnable(self._structured_result)


class TestRecommendationV0ReActGenerationAgent(unittest.TestCase):
    def test_invoke_formats_prompt_inputs_and_returns_structured_output(self) -> None:
        structured_output = AgentOutput(
            system_response="Recommendation_v0 is still a template, so I do not have concrete matches yet.",
            recommendations=[RecommendationV0(region_id="pt-faro", explanation="Coastal and budget-friendly option based on the embedded catalog data.")],
        )
        fake_llm = _FakeChatModel(structured_output)
        history_row = ChatRecord(
            user_id=UUID("11111111-1111-1111-1111-111111111111"),
            session_id=UUID("22222222-2222-2222-2222-222222222222"),
            chat_history_number=0,
            user_request="Need somewhere warm",
            system_response="Consider southern Europe",
            synthesized_query="warm beach in Europe",
            recommendations=[],
            graph_version="recommendation_v0",
        )

        agent = module.RecommendationV0ReActGenerationAgent(
            llm=fake_llm,
        )

        result = agent.invoke(
            user_input="Same vibe, but cheaper and near the beach",
            included_region_ids=["pt-faro"],
            excluded_region_ids=["es-ibiza"],
            history=[history_row],
        )

        self.assertEqual(result, structured_output)
        self.assertEqual(len(agent._structured_output_llm.invocations), 1)
        messages = agent._structured_output_llm.invocations[0]
        self.assertEqual(len(messages), 2)
        self.assertIn("prompt-only recommendation step", str(messages[0].content))
        self.assertIn("only source of truth", str(messages[0].content))
        self.assertIn("Latest user request", str(messages[1].content))
        self.assertIn("Same vibe, but cheaper and near the beach", str(messages[1].content))
        self.assertIn("Need somewhere warm", str(messages[1].content))
        self.assertIn("pt-faro", str(messages[1].content))
        self.assertIn("es-ibiza", str(messages[1].content))
        self.assertIn("Travel catalog data", str(messages[1].content))

    def test_invoke_sends_prompt_messages_to_structured_llm(self) -> None:
        structured_output = AgentOutput(
            system_response="Recommendation_v0 is grounded in the embedded dataset.",
            recommendations=[RecommendationV0(region_id="pt-faro", explanation="Warm coastal option visible in the embedded catalog data.")],
        )
        fake_llm = _FakeChatModel(structured_output)
        agent = module.RecommendationV0ReActGenerationAgent(
            llm=fake_llm,
        )

        result = agent.invoke(user_input="I want to do some water sports")

        self.assertEqual(result, structured_output)
        self.assertEqual(len(agent._structured_output_llm.invocations), 1)


if __name__ == "__main__":
    unittest.main()
