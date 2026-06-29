FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml ./
RUN uv sync --no-dev

COPY . .

EXPOSE 8000

# Default command runs the FastAPI health app; the bot and the Celery
# worker override this via docker-compose `command:`.
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
