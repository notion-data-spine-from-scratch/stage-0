#!/usr/bin/env bash
set -euo pipefail

# scripts/qa_smoke_test.sh
# Run Stage E-04 smoke tests for local QA.

COMPOSE_FULL="compose/full.yml"
COMPOSE_SPINE="compose/spine-only.yml"

# 1. Rebuild images and bring up services
printf '\n[1/7] Build and start services...\n'
docker compose -f "$COMPOSE_FULL" build --pull
docker compose -f "$COMPOSE_FULL" up -d

# 2. Unit & API test suite
printf '\n[2/7] Running unit & API tests...\n'
docker compose -f "$COMPOSE_FULL" exec api pytest -q

# 3. Endpoint-specific integration check
printf '\n[3/7] Running /blocks/{id}/ops integration test...\n'
docker compose -f "$COMPOSE_FULL" exec api \
    pytest tests/test_api_ops.py::test_ops_success_and_conflict

# 4. Seed-data smoke test
printf '\n[4/7] Generating seed data...\n'
docker compose -f "$COMPOSE_SPINE" run --rm \
    -e DSN='postgresql://notion:notion@db:5432/notion' \
    api \
    python -m scripts.generate_seed --users 20 --workspaces 3 --blocks 200000

# 5. gRPC service health
printf '\n[5/7] Checking gRPC service health...\n'
docker compose -f "$COMPOSE_FULL" exec crdt \
    python /usr/local/bin/healthcheck.py

# 6. HTTP API health
printf '\n[6/7] Checking HTTP API health...\n'
curl -sf http://localhost:8000/health

# 7. Load / smoke testing
printf '\n[7/7] Running load test with Locust...\n'
poetry run locust -f tests/locustfile.py --headless -u 1 -r 1 -t 10s

printf '\nQA smoke tests complete.\n'
