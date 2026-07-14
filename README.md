# Travel Recommender

A conversational travel recommendation app that helps users discover destinations through a hybrid interface. The assistant streams recommendations, stores destination data in PostgreSQL with `pgvector`, and shows suggested regions on an interactive map.

## Project structure

| Path | Purpose |
| --- | --- |
| `backend/` | FastAPI API, LangGraph recommendation flow, storage layer, migrations, and data bootstrap scripts. |
| `frontend/` | React + Vite client with chat, map, recommendation display, and optional survey UI. |
| `infrastructure/application/` | Docker Compose setup for running the built backend and frontend containers. |
| `evaluation/` | Synthetic queries, generated results, and user-study data. |

## Tech Stack

- Backend: FastAPI, LangGraph, SQLModel, PostgreSQL, `pgvector`
- Frontend: React, TypeScript, Vite, Material UI, Leaflet
- Models: Ollama or OpenAI-compatible LLM and embedding providers

## Prerequisites

To run the application, you need:

- Docker and Docker Compose.
- A PostgreSQL database with the `pgvector` extension enabled.
- An LLM endpoint reachable from the backend container.
- An embedding model endpoint reachable from the backend container.

## Docker Start

### 1. Create the Environment File

Copy the example application environment file:

```bash
cp infrastructure/application/.env.example infrastructure/application/.env
```

### 2. Configure External Services

Edit `infrastructure/application/.env` and set the service connection details.

Set the PostgreSQL connection string:

```env
STORAGE_ENGINE__DB_URL=postgresql+psycopg://user:password@postgres-host:5432/recommender
```

Configure the LLM provider:

```env
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1
LLM_BASE_URL=http://llm-host:11434
LLM_API_KEY=
```

Configure the embedding provider:

```env
EMBEDDINGS_PROVIDER=ollama
EMBEDDINGS_MODEL_NAME=nomic-embed-text
EMBEDDINGS_BASE_URL=http://embedding-host:11434
EMBEDDINGS_API_KEY=
```

Set API and frontend URLs if you changed the default published ports:

```env
BACKEND_PORT=8000
FRONTEND_PORT=8080
API_CORS_ALLOW_ORIGINS=http://localhost:8080
API_BASE_URL=http://localhost:8000
```

`TAVILY_API_KEY` is optional. Without it, web-search based destination exploration may be unavailable.

### 3. Start the Application

Build and start the backend and frontend containers:

```bash
docker compose --env-file infrastructure/application/.env -f infrastructure/application/docker-compose.yml up --build
```

Default URLs:

- Frontend: `http://localhost:8080`
- Backend: `http://localhost:8000`

### 4. Seed Destination Data

Run this after the application is started and the embedding provider is reachable:

```bash
docker compose --env-file infrastructure/application/.env -f infrastructure/application/docker-compose.yml exec backend python -m storage.bootstrap_travel_destinations
```
