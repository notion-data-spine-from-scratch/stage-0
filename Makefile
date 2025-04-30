# Makefile · Stage-0 spine-only targets

# Path to our Compose file
COMPOSE_FILE := compose/spine-only.yml
COMPOSE_CMD  := docker compose -f $(COMPOSE_FILE)

.PHONY: up down

# Build and start the spine-only stack in detached mode
up:
	$(COMPOSE_CMD) up -d --build

# Tear down the spine-only stack
down:
	$(COMPOSE_CMD) down
seed:
    @export DSN="postgres://notion:notion@localhost:5433/notion" && \
    poetry run python scripts/generate_seed.py --users 20 --workspaces 3 --blocks 200000
