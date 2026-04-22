from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

sys.path.append(str(Path(__file__).resolve().parents[3]))

from embeddings.configuration import OllamaTextEmbeddingModelConfiguration
from embeddings.ollama_text_embedding_model import OllamaTextEmbeddingModel

TEST_EMBEDDINGS_MODEL_NAME = "nomic-embed-text"
TEST_EMBEDDINGS_BASE_URL = "http://localhost:11434"


class TestOllamaTextEmbeddingModelE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if os.environ.get("RUN_EMBEDDINGS_E2E") != "1":
            raise unittest.SkipTest("Set RUN_EMBEDDINGS_E2E=1 to run embeddings e2e tests")

        configuration = OllamaTextEmbeddingModelConfiguration(
            model_name=TEST_EMBEDDINGS_MODEL_NAME,
            base_url=TEST_EMBEDDINGS_BASE_URL,
        )

        tags_endpoint = f"{configuration.base_url.rstrip('/')}/api/tags"
        try:
            with urlopen(tags_endpoint, timeout=5) as response:  # noqa: S310
                status_code = response.getcode()
        except URLError as error:
            raise unittest.SkipTest(
                f"Ollama endpoint is not reachable at {configuration.base_url}: {error}"
            ) from error

        if status_code != 200:
            raise unittest.SkipTest(
                f"Ollama endpoint returned unexpected status code {status_code} at {tags_endpoint}"
            )

        cls.embedding_model = OllamaTextEmbeddingModel(configuration)

    def test_embed_query_returns_non_empty_float_vector(self) -> None:
        embedding = self.embedding_model.embed_query("Weekend trip with nature and hikes")

        self.assertGreater(len(embedding), 0)
        self.assertTrue(all(isinstance(value, float) for value in embedding))

    def test_dimension_matches_embedding_length(self) -> None:
        embedding = self.embedding_model.embed_query("City break with museums")

        self.assertEqual(self.embedding_model.get_dimentions(), len(embedding))

    def test_dimension_is_stable_across_multiple_queries(self) -> None:
        queries = [
            "Beach destination with calm weather",
            "Budget friendly mountain holiday",
            "Culture and architecture focused city trip",
        ]

        dimensions = [len(self.embedding_model.embed_query(query)) for query in queries]
        self.assertTrue(all(dimension == self.embedding_model.get_dimentions() for dimension in dimensions))

    def test_get_dimentions_returns_positive_integer(self) -> None:
        self.assertIsInstance(self.embedding_model.get_dimentions(), int)
        self.assertGreater(self.embedding_model.get_dimentions(), 0)

    def test_embed_query_rejects_blank_text(self) -> None:
        with self.assertRaises(ValueError):
            self.embedding_model.embed_query("   ")

    def test_check_health_returns_true_for_reachable_ollama(self) -> None:
        self.assertTrue(self.embedding_model.check_health())


if __name__ == "__main__":
    unittest.main()
