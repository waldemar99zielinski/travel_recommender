FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.8.15 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    API_ENV=production \
    API_HOST=0.0.0.0 \
    API_PORT=80

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src

EXPOSE 80

CMD ["uv", "run", "uvicorn", "api.main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "80"]
