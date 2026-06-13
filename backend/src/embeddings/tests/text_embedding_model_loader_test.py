from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[2]))

from embeddings.configuration import TextEmbeddingModelConfiguration
from embeddings.loader import create_text_embedding_model


class TestTextEmbeddingModelLoader(unittest.TestCase):
    @patch("embeddings.loader.OllamaTextEmbeddingModel")
    def test_create_text_embedding_model_returns_ollama_model(self, ollama_model_class) -> None:
        expected_model = object()
        ollama_model_class.return_value = expected_model
        configuration = TextEmbeddingModelConfiguration(
            provider="ollama",
            model_name="nomic-embed-text",
            base_url="http://localhost:11434",
        )

        embedding_model = create_text_embedding_model(configuration)

        ollama_model_class.assert_called_once_with(configuration)
        self.assertIs(embedding_model, expected_model)

    @patch("embeddings.loader.OpenAITextEmbeddingModel")
    def test_create_text_embedding_model_returns_openai_model(self, openai_model_class) -> None:
        expected_model = object()
        openai_model_class.return_value = expected_model
        configuration = TextEmbeddingModelConfiguration(
            provider="openai",
            model_name="text-embedding-3-small",
            api_key="sk-test",
        )

        embedding_model = create_text_embedding_model(configuration)

        openai_model_class.assert_called_once_with(configuration)
        self.assertIs(embedding_model, expected_model)


if __name__ == "__main__":
    unittest.main()
