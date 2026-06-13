from __future__ import annotations

import unittest
from unittest import mock
from uuid import UUID

from langchain_core.messages import AIMessage

from recommender.graphs.recommendation_v1.agents import recommendation_v1_generation_react_agent as module
from recommender.graphs.recommendation_v1.agents.recommendation_v1_generation_models import AgentOutput
from recommender.graphs.recommendation_v1.models import RecommendationV1
from storage.models.chat_record import ChatRecord


class _FakeRunnable:
    def __init__(self, result: object) -> None:
        self._result = result
        self.invocations: list[dict[str, object]] = []

    def invoke(self, inputs: dict[str, object]) -> object:
        self.invocations.append(inputs)
        return self._result


class _FakeChatModel:
    def __init__(self, structured_result: AgentOutput) -> None:
        self._structured_result = structured_result

    def with_structured_output(self, _output_type: object) -> _FakeRunnable:
        return _FakeRunnable(self._structured_result)


class TestRecommendationV1ReActGenerationAgent(unittest.TestCase):
    def test_invoke_formats_prompt_inputs_and_returns_structured_output(self) -> None:
        structured_output = AgentOutput(
            system_response="Try Faro for a cheaper sunny beach trip.",
            recommendations=[RecommendationV1(region_id="pt-faro", explanation="Cheaper coastal option with a sunny beach feel.")],
        )
        fake_runnable = _FakeRunnable({"structured_response": structured_output})
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

        with (
            mock.patch.object(
                module,
                "create_travel_destination_sql_query_tool",
                return_value=mock.sentinel.destination_sql_tool,
            ) as create_destination_tool_mock,
            mock.patch.object(module, "create_agent", return_value=fake_runnable) as create_agent_mock,
        ):
            agent = module.RecommendationV1ReActGenerationAgent(
                llm=fake_llm,
                db_engine=mock.sentinel.db_engine,
            )

        result = agent.invoke(
            user_input="Same vibe, but cheaper and near the beach",
            included_region_ids=["pt-faro"],
            excluded_region_ids=["es-ibiza"],
            history=[history_row],
        )

        self.assertEqual(result, structured_output)
        create_destination_tool_mock.assert_called_once_with(
            mock.sentinel.db_engine,
        )
        create_agent_mock.assert_called_once_with(
            model=fake_llm,
            tools=[mock.sentinel.destination_sql_tool],
            response_format=AgentOutput,
            debug=True,
        )
        self.assertEqual(len(fake_runnable.invocations), 1)
        messages = fake_runnable.invocations[0]["messages"]
        self.assertEqual(len(messages), 2)
        self.assertIn("execute_travel_destination_sql_query", str(messages[0].content))
        self.assertIn("travel_destinations table structure", str(messages[0].content))
        self.assertIn("Latest user request", str(messages[1].content))
        self.assertIn("Same vibe, but cheaper and near the beach", str(messages[1].content))
        self.assertIn("Need somewhere warm", str(messages[1].content))
        self.assertIn("pt-faro", str(messages[1].content))
        self.assertIn("es-ibiza", str(messages[1].content))

    def test_invoke_falls_back_to_structured_output_pass_when_state_lacks_structured_response(self) -> None:
        structured_output = AgentOutput(
            system_response="Faro is a strong fit for water sports.",
            recommendations=[RecommendationV1(region_id="pt-faro", explanation="Strong water sports match with coastal conditions.")],
        )
        fake_llm = _FakeChatModel(structured_output)
        fake_runnable = _FakeRunnable(
            {"messages": [AIMessage(content="Faro looks like a strong option for water sports.")]}
        )

        with (
            mock.patch.object(module, "create_travel_destination_sql_query_tool", return_value=mock.sentinel.destination_sql_tool),
            mock.patch.object(module, "create_agent", return_value=fake_runnable),
        ):
            agent = module.RecommendationV1ReActGenerationAgent(
                llm=fake_llm,
                db_engine=mock.sentinel.db_engine,
            )

        result = agent.invoke(user_input="I want to do some water sports")

        self.assertEqual(result, structured_output)


if __name__ == "__main__":
    unittest.main()
