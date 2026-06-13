from __future__ import annotations

import unittest
from typing import Any
from typing import cast
from unittest import mock
from uuid import UUID

from recommender.graphs.recommendation_v1 import recommendation_v1_graph as module
from recommender.graphs.recommendation_v1.agents.recommendation_v1_generation_models import AgentOutput
from recommender.graphs.recommendation_v1.models import RecommendationV1
from recommender.graphs.recommendation_v1.models import RecommendationV1GraphState
from recommender.models.session.session import Session
from storage.models.chat_record import ChatRecord
from storage.stores.chat_store import ChatStore
from storage.stores.travel_destination_store import TravelDestinationStore


class _FakeChatStore:
    def __init__(self, history_rows: list[ChatRecord]) -> None:
        self._history_rows = history_rows
        self.load_calls: list[dict[str, str]] = []
        self.upserted_rows: list[ChatRecord] = []

    def load_session(self, user_id: str, session_id: str) -> list[ChatRecord]:
        self.load_calls.append({"user_id": user_id, "session_id": session_id})
        return list(self._history_rows)

    def upsert_many(self, rows: list[ChatRecord]) -> None:
        self.upserted_rows.extend(rows)


class _FakeTravelDestinationStore:
    pass


class _FakeGenerationAgent:
    def __init__(self, output: AgentOutput) -> None:
        self._output = output
        self.invocations: list[dict] = []

    def invoke(self, **kwargs) -> AgentOutput:
        self.invocations.append(kwargs)
        return self._output


class _FakeCompiledGraph:
    def __init__(self, nodes: dict[str, object], edges: list[tuple[object, object]]) -> None:
        self._nodes = nodes
        self._edges = edges

    def invoke(self, state: dict[str, Any]) -> dict[str, Any]:
        current_state = dict(state)
        current_node: object = "START"

        while True:
            next_nodes = [target for source, target in self._edges if source == current_node]
            if len(next_nodes) != 1:
                raise AssertionError(f"Expected one outgoing edge from {current_node!r}, got {next_nodes!r}")

            next_node = next_nodes[0]
            if next_node == "END":
                return current_state

            node_callable = self._nodes[next_node]
            state_model = RecommendationV1GraphState(**current_state)  # type: ignore[arg-type]
            node_output = node_callable(state_model)
            current_state = {**current_state, **node_output}
            current_node = next_node


class _FakeStateGraph:
    last_instance: _FakeStateGraph | None = None

    def __init__(self, _state_type: object) -> None:
        self.nodes: dict[str, object] = {}
        self.edges: list[tuple[object, object]] = []
        _FakeStateGraph.last_instance = self

    def add_node(self, name: str, node_callable) -> None:
        self.nodes[name] = node_callable

    def add_edge(self, source: object, target: object) -> None:
        self.edges.append((source, target))

    def compile(self) -> _FakeCompiledGraph:
        return _FakeCompiledGraph(self.nodes, self.edges)


class TestRecommendationV1Graph(unittest.TestCase):
    def test_build_graph_creates_single_node_that_loads_history_and_persists_turn(self) -> None:
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
        recommendation = RecommendationV1(
            region_id="pt-faro",
            explanation="Sunny coastal escape with a strong beach match.",
        )
        fake_agent = _FakeGenerationAgent(
            AgentOutput(
                system_response="Try Faro for a sunny coastal escape.",
                recommendations=[recommendation],
            )
        )
        session_store = _FakeChatStore([history_row])
        travel_store = _FakeTravelDestinationStore()
        emitted_events: list[dict[str, object]] = []

        with (
            mock.patch.object(module, "StateGraph", _FakeStateGraph),
            mock.patch.object(module, "START", "START"),
            mock.patch.object(module, "END", "END"),
            mock.patch(
                "recommender.graphs.recommendation_v1.stream_events.get_stream_writer",
                return_value=emitted_events.append,
            ),
            mock.patch.object(
                module,
                "RecommendationV1ReActGenerationAgent",
                return_value=fake_agent,
            ) as recommendation_agent_mock,
            mock.patch.object(module, "create_llm_chat_model", return_value=mock.sentinel.llm),
        ):
            graph = cast(
                Any,
                module.build_recommendation_v1_graph(
                    travel_destination_store=cast(TravelDestinationStore, travel_store),
                    recommendation_session_store=cast(ChatStore, session_store),
                    db_engine=mock.sentinel.engine,
                ),
            )

        recommendation_agent_mock.assert_called_once_with(
            llm=mock.sentinel.llm,
            db_engine=mock.sentinel.engine,
        )

        graph_result = graph.invoke(
            {
                "session": Session(
                    user_id="11111111-1111-1111-1111-111111111111",
                    session_id="22222222-2222-2222-2222-222222222222",
                ),
                "user_request": "Same vibe, but cheaper and near the beach",
            }
        )

        self.assertIsNotNone(_FakeStateGraph.last_instance)
        state_graph = _FakeStateGraph.last_instance
        assert state_graph is not None
        self.assertEqual(len(state_graph.nodes), 3)
        self.assertEqual(
            session_store.load_calls,
            [
                {
                    "user_id": "11111111-1111-1111-1111-111111111111",
                    "session_id": "22222222-2222-2222-2222-222222222222",
                }
            ],
        )
        self.assertEqual(len(fake_agent.invocations), 1)
        self.assertEqual(fake_agent.invocations[0]["user_input"], "Same vibe, but cheaper and near the beach")
        self.assertEqual(graph_result["recommendations"], [recommendation])
        self.assertIsInstance(graph_result["system_response"], str)
        self.assertTrue(graph_result["system_response"].strip())
        self.assertEqual(len(session_store.upserted_rows), 1)
        persisted_row = session_store.upserted_rows[0]
        self.assertEqual(persisted_row.graph_version, "v1")
        self.assertEqual(persisted_row.chat_history_number, 1)
        self.assertEqual(persisted_row.user_request, "Same vibe, but cheaper and near the beach")
        self.assertEqual(persisted_row.synthesized_query, "Same vibe, but cheaper and near the beach")
        self.assertEqual(graph_result["history"][-1], persisted_row)
        self.assertEqual(
            emitted_events,
            [
                {"event": "init", "data": {}},
                {
                    "event": "recommendation",
                    "data": {
                        "user_id": "11111111-1111-1111-1111-111111111111",
                        "session_id": "22222222-2222-2222-2222-222222222222",
                        "chat_history_number": 1,
                        "user_request": "Same vibe, but cheaper and near the beach",
                        "system_response": "Try Faro for a sunny coastal escape.",
                        "recommendations": [
                            {
                                "region_id": "pt-faro",
                                "explanation": "Sunny coastal escape with a strong beach match.",
                            }
                        ],
                        "travel_destinations_evaluations": [],
                        "included_regions_ids": [],
                        "excluded_regions_ids": [],
                    },
                },
                {"event": "completed", "data": {}},
            ],
        )


if __name__ == "__main__":
    unittest.main()
