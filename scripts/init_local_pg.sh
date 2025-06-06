#!/usr/bin/env bash
set -euo pipefail

# scripts/init_local_pg.sh
# Bootstrap a local Postgres 16 cluster on port 5433 with the Stage-0 schema.

CLUSTER="notion-test"
PORT=5433

# Recreate cluster from scratch
sudo pg_dropcluster --stop -f 16 "$CLUSTER" >/dev/null 2>&1 || true
sudo pg_createcluster --start 16 "$CLUSTER" --port=$PORT

# Create user + database
sudo -u postgres psql -p $PORT -c "CREATE USER notion WITH PASSWORD 'notion';" >/dev/null
sudo -u postgres psql -p $PORT -c "CREATE DATABASE notion OWNER notion;" >/dev/null

# Load schema files
sudo -u postgres psql -p $PORT -d notion -f db/01-schema.sql >/dev/null
sudo -u postgres psql -p $PORT -d notion -f db/02-plans.sql >/dev/null

# Grant ownership to notion
sudo -u postgres psql -p $PORT -d notion -c "ALTER TABLE users OWNER TO notion;" >/dev/null
sudo -u postgres psql -p $PORT -d notion -c "ALTER TABLE workspaces OWNER TO notion;" >/dev/null
sudo -u postgres psql -p $PORT -d notion -c "ALTER TABLE blocks OWNER TO notion;" >/dev/null
sudo -u postgres psql -p $PORT -d notion -c "ALTER TABLE plans OWNER TO notion;" >/dev/null
sudo -u postgres psql -p $PORT -d notion -c "ALTER TABLE workspace_plans OWNER TO notion;" >/dev/null
sudo -u postgres psql -p $PORT -d notion -c "ALTER TABLE block_acl OWNER TO notion;" >/dev/null

# Insert a seed user + workspace so tests can run
sudo -u postgres psql -p $PORT -d notion -c "INSERT INTO users (email, hashed_password) VALUES ('seed@example.com', 'pw');" >/dev/null
sudo -u postgres psql -p $PORT -d notion -c "INSERT INTO workspaces (owner_id, name) SELECT id, 'seed-ws' FROM users LIMIT 1;" >/dev/null

echo "Local Postgres cluster '$CLUSTER' running on port $PORT with seed data."
