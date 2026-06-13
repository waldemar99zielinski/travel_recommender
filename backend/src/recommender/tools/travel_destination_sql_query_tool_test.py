from __future__ import annotations

import json
import unittest
from datetime import datetime
from datetime import timezone

from recommender.tools import travel_destination_sql_query_tool as module


class _FakeMappingsResult:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self._rows = rows

    def all(self) -> list[dict[str, object]]:
        return list(self._rows)


class _FakeExecutionResult:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self._rows = rows

    def mappings(self) -> _FakeMappingsResult:
        return _FakeMappingsResult(self._rows)


class _FakeConnection:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self._rows = rows
        self.executed_statements: list[object] = []

    def __enter__(self) -> _FakeConnection:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        del exc_type, exc, tb

    def execute(self, statement: object) -> _FakeExecutionResult:
        self.executed_statements.append(statement)
        return _FakeExecutionResult(self._rows)


class _FakeEngine:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.connection = _FakeConnection(rows)

    def connect(self) -> _FakeConnection:
        return self.connection


class TestTravelDestinationSQLQueryTool(unittest.TestCase):
    def test_tool_executes_query_and_serializes_results(self) -> None:
        engine = _FakeEngine(
            [
                {
                    "id": "pt-faro",
                    "region": "Faro",
                    "cost_per_week": 780.0,
                    "updated_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
                }
            ]
        )
        tool = module.create_travel_destination_sql_query_tool(engine)

        output = tool.invoke(
            {
                "sql_query": "SELECT id, region, cost_per_week, updated_at FROM travel_destinations ORDER BY cost_per_week ASC LIMIT 5"
            }
        )

        self.assertEqual(len(engine.connection.executed_statements), 1)
        payload = json.loads(output)
        self.assertEqual(payload[0]["id"], "pt-faro")
        self.assertEqual(payload[0]["updated_at"], "2026-01-01T00:00:00+00:00")

    def test_tool_rejects_non_select_queries(self) -> None:
        engine = _FakeEngine([])
        tool = module.create_travel_destination_sql_query_tool(engine)

        with self.assertRaises(ValueError):
            tool.invoke({"sql_query": "DELETE FROM travel_destinations"})


if __name__ == "__main__":
    unittest.main()
