# tests/conftest.py

import os

# Force tests to hit localhost:5433 (your mapped Postgres port)
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://notion:notion@localhost:5433/notion"
)
