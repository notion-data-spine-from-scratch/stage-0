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

# Install all deps (main + dev) so pytest, ruff, etc. are available
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi --with dev --no-root

# Copy application code and services
COPY src/      ./src/
COPY services/ ./services/
COPY tests/    ./tests/
COPY scripts/  ./scripts/

# Copy pytest config so the container sees your markers
COPY pytest.ini ./pytest.ini

# ---------- Runtime stage ----------
FROM python:3.12-slim

# Create a non-root user
RUN useradd --create-home appuser

USER appuser
WORKDIR /home/appuser/code

# Bring over installed packages & tooling
COPY --from=builder /usr/local/lib/python3.12/site-packages/ \
     /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy our FastAPI app and the gRPC services client code
COPY --from=builder --chown=appuser:appuser /code/src/app/.          ./app/
COPY --from=builder --chown=appuser:appuser /code/src/search_worker/. ./search_worker/
COPY --from=builder --chown=appuser:appuser /code/services/.         ./services/
COPY --from=builder --chown=appuser:appuser /code/tests/.            ./tests/
COPY --from=builder --chown=appuser:appuser /code/scripts/.          ./scripts/

# Also bring in pytest.ini for marker registration
COPY --from=builder --chown=appuser:appuser /code/pytest.ini     ./pytest.ini

# Disable Python output buffering
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Start up by seeding the database then launching Uvicorn
CMD ["./scripts/seed_then_start.sh"]
