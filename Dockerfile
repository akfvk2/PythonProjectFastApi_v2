FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_VERSION=1.9.0

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir poetry==$POETRY_VERSION

COPY pyproject.toml poetry.lock* ./

RUN poetry install --only main --no-root --no-ansi && rm -rf $POETRY_CACHE_DIR


FROM python:3.12-slim
LABEL authors="Александр"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN groupadd -r myuser && useradd -m -r -g myuser myuser

COPY --from=builder --chown=myuser:myuser /app/.venv /app/.venv

COPY --chown=myuser:myuser src ./src
COPY --chown=myuser:myuser alembic ./alembic
COPY --chown=myuser:myuser alembic.ini ./

USER myuser

EXPOSE 8001

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001", "--factory"]