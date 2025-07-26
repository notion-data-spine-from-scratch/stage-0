#!/usr/bin/env bash
set -e

echo "⏳ Seeding database…"
python scripts/generate_seed.py || true

echo "🚀 Starting API server…"
exec uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000
