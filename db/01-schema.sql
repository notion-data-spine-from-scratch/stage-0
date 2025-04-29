-- Enable UUID generation for primary keys
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ──────────────────────────────────────────────────────────────────────────────
-- Users
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE users (
  id              UUID           PRIMARY KEY DEFAULT uuid_generate_v4(),
  email           TEXT           NOT NULL UNIQUE,
  hashed_password TEXT           NOT NULL,
  created_at      TIMESTAMPTZ    NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ    NOT NULL DEFAULT now()
);

-- ──────────────────────────────────────────────────────────────────────────────
-- Workspaces
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE workspaces (
  id           UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
  owner_id     UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name         TEXT        NOT NULL,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_workspaces_owner_id ON workspaces(owner_id);

-- ──────────────────────────────────────────────────────────────────────────────
-- Blocks
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE blocks (
  id            UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
  parent_id     UUID        REFERENCES blocks(id) ON DELETE CASCADE,
  workspace_id  UUID        NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  type          TEXT        NOT NULL,
  props         JSONB       NOT NULL DEFAULT '{}'::jsonb,
  version       BIGINT      NOT NULL DEFAULT 1,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes for performance
CREATE INDEX idx_blocks_workspace_id ON blocks(workspace_id);
CREATE INDEX idx_blocks_parent_id    ON blocks(parent_id);
CREATE INDEX idx_blocks_props_gin     ON blocks USING GIN (props);

-- Trigger to enforce version bump and update timestamp
CREATE FUNCTION block_version_trigger_fn() RETURNS trigger AS $$
BEGIN
  IF NEW.version <= OLD.version THEN
    RAISE EXCEPTION 'block.version must increase on update';
  END IF;
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_blocks_version
  BEFORE UPDATE ON blocks
  FOR EACH ROW EXECUTE FUNCTION block_version_trigger_fn();

