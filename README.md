# Notion Data-Spine Stage-0

This repo is the **Stage 0 “Garage Prototype”** of the Notion Data-Spine project—a 2016-era mini-Notion, including:

- **FastAPI** service for block CRUD & WebSocket echo  
- **Postgres** schema for blocks, users, workspaces, ACLs, plans  
- **Redis** hot-path cache  
- **Automerge** CRDT merge service  
- **Kafka** + WebSocket fan-out  
- **Meilisearch** indexing & search API  
- **Asset proxy** (NGINX+Lua + thumbnail lambda)  
- **Auth** (Ory Kratos) & **Billing** (Stripe webhook)  
- **Observability** (Prometheus, Grafana dashboards)

## Getting Started

Requires **Python&nbsp;3.12** with [Poetry](https://python-poetry.org/).

1. Copy `.env.example` → `.env` and fill in keys. The sample values
   mirror the Docker Compose services (Postgres on `5433`, Redis on
   `6379`, CRDT gRPC on `50051`).
2. `poetry install`
3. (Optional) `./scripts/init_local_pg.sh` to spin up a local Postgres
   cluster on port `5433` with seed data. Alternatively run `make up`
   to start the full Docker Compose stack.
4. `pytest`

Optionally run `poetry run pre-commit run --all-files` to lint and format
the codebase.

### QA Smoke Tests
Run `./scripts/qa_smoke_test.sh` to rebuild images, start services, run tests and verify the health endpoints with a short load test.

## Roadmap

We’re tracking every commit-level task in the **Stage-0** Project board.  




Stay Tuned !

