#-------------- builder stage ----------
FROM python:3.12-slim AS builder

# Install build tools
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
 && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy lockfiles to leverage cache
COPY pyproject.toml poetry.lock ./

# Install dependencies only (skip the project itself)
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi --only main --no-root

# Copy all source
COPY src/ ./src/

# ---------- Runtime stage ----------
FROM python:3.12-slim

# Create a non-root user
RUN useradd --create-home appuser


USER appuser
WORKDIR /home/appuser/code

# Copy dependencies & entrypoints
COPY --from=builder /usr/local/lib/python3.12/site-packages/ \
     /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Flatten src/app → app/
COPY --from=builder --chown=appuser:appuser /code/src/app/. ./app/

# Disable Python output buffering
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Launch via Uvicorn pointing at app.main:create_app
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]

