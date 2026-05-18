from __future__ import annotations

import unittest
from uuid import UUID
from uuid import uuid4

from storage.identifiers import normalize_identifier_to_uuid


class TestNormalizeIdentifierToUuid(unittest.TestCase):
    def test_returns_uuid_values_unchanged(self) -> None:
        identifier = uuid4()

        self.assertEqual(
            normalize_identifier_to_uuid(identifier, field_name="user_id"),
            identifier,
        )

    def test_parses_uuid_formatted_strings(self) -> None:
        identifier = str(uuid4())

        self.assertEqual(
            normalize_identifier_to_uuid(identifier, field_name="session_id"),
            UUID(identifier),
        )

    def test_maps_non_uuid_strings_to_stable_uuid(self) -> None:
        left = normalize_identifier_to_uuid("session-abc", field_name="session_id")
        right = normalize_identifier_to_uuid("session-abc", field_name="session_id")

        self.assertEqual(left, right)

    def test_field_name_affects_non_uuid_mapping(self) -> None:
        user_id = normalize_identifier_to_uuid("shared-value", field_name="user_id")
        session_id = normalize_identifier_to_uuid("shared-value", field_name="session_id")

        self.assertNotEqual(user_id, session_id)

    def test_rejects_empty_strings(self) -> None:
        with self.assertRaisesRegex(ValueError, "user_id must not be empty"):
            normalize_identifier_to_uuid("   ", field_name="user_id")


if __name__ == "__main__":
    unittest.main()
