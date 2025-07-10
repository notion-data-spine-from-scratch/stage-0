# tests/conftest.py

import os
import socket
import sys
from pathlib import Path

import pytest

# Force tests to hit localhost:5433 (your mapped Postgres port)
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://notion:notion@localhost:5433/notion"
)

# Ensure the repository root (for `services` package) is on sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))


def _db_available() -> bool:
    """Return True if a PostgreSQL instance appears reachable."""
    try:
        sock = socket.create_connection(("localhost", 5433), timeout=1)
        sock.close()
        return True
    except OSError:
        return False


DB_AVAILABLE = _db_available()


# def pytest_runtest_setup(item: pytest.Item) -> None:  # pragma: no cover - hook
#     if "db" in item.keywords and not DB_AVAILABLE:
#         pytest.skip("PostgreSQL not available", allow_module_level=True)
