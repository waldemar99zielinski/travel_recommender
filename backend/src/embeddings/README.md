# Embeddings Package

This package provides the Ollama-backed embedding model and configuration used by the backend.

## Test structure

- E2E tests live in `src/embeddings/tests/e2e/`.
- Main suite file: `src/embeddings/tests/e2e/ollama_text_embedding_model_e2e_test.py`.

## Prerequisites for E2E tests

Set these environment variables (for example in `backend/.env`):

- `EMBEDDINGS_MODEL_NAME` (example: `nomic-embed-text`)
- `EMBEDDINGS_BASE_URL` (example: `http://localhost:11434`)

Start Ollama and ensure the embedding model is available locally.

## Running tests

From the `backend/` directory:

```bash
uv run python -m unittest discover -s src/embeddings/tests/e2e -p "*test*.py" -v
```

If you run commands from the repository root, use `uv --directory backend ...`:

```bash
uv --directory backend run python -m unittest discover -s src/embeddings/tests/e2e -p "*test*.py" -v
```

By default, E2E tests are skipped unless explicitly enabled.

Enable and run E2E tests:

```bash
RUN_EMBEDDINGS_E2E=1 uv run python -m unittest discover -s src/embeddings/tests/e2e -p "*test*.py" -v
```

Run a single E2E test module:

```bash
RUN_EMBEDDINGS_E2E=1 uv run python -m unittest src.embeddings.tests.e2e.ollama_text_embedding_model_e2e_test -v
```

## What the E2E suite validates

- `embed_query` returns a non-empty vector of floats
- reported dimension from `get_dimentions()` matches returned embedding length
- dimension from `get_dimentions()` stays stable across multiple queries
- blank input is rejected with a `ValueError`
- `check_health()` returns `True` when Ollama is reachable and responding

## Troubleshooting

- If you see a skip saying `Set RUN_EMBEDDINGS_E2E=1`, export that variable before running tests.
- If you see a skip about missing configuration, set `EMBEDDINGS_MODEL_NAME` and `EMBEDDINGS_BASE_URL`.
- If you see a skip about Ollama endpoint reachability, verify Ollama is running and accessible at `EMBEDDINGS_BASE_URL`.
