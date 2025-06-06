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

1. Copy `.env.example` → `.env` and fill in keys. The sample values
   mirror the Docker Compose services (Postgres on `5433`, Redis on
   `6379`, CRDT gRPC on `50051`).
2. `docker compose -f compose/spine-only.yml up --build -d`  
3. `pytest` passes on your local  

## Roadmap

We’re tracking every commit-level task in the **Stage-0** Project board.  




Stay Tuned !

