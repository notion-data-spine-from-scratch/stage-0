-- plans.sql
-- Billingg Plans
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE plans (
	  id          SERIAL        PRIMARY KEY,
	  name        TEXT          NOT NULL UNIQUE,
	  max_blocks  BIGINT        NOT NULL,      -- quota per workspace
	  price_cents INTEGER       NOT NULL,      -- monthly price in cents
	  created_at  TIMESTAMPTZ   NOT NULL DEFAULT now()
);

-- ──────────────────────────────────────────────────────────────────────────────
-- Workspace Subscriptions
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TABLE workspace_plans (
	  workspace_id UUID         NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
	  plan_id      INTEGER      NOT NULL REFERENCES plans(id) ON DELETE RESTRICT,
	  started_at   TIMESTAMPTZ  NOT NULL DEFAULT now(),
	  PRIMARY KEY (workspace_id)
);

-- ──────────────────────────────────────────────────────────────────────────────
-- Row-level Access Control (ACL)
-- ──────────────────────────────────────────────────────────────────────────────
CREATE TYPE acl_right AS ENUM ('read','write','admin');

CREATE TABLE block_acl (
	  block_id   UUID          NOT NULL REFERENCES blocks(id) ON DELETE CASCADE,
	  subject_id UUID          NOT NULL REFERENCES users(id)  ON DELETE CASCADE,
	  rights     acl_right[]   NOT NULL DEFAULT ARRAY['read']::acl_right[],
	  PRIMARY KEY (block_id, subject_id)
);

CREATE INDEX idx_block_acl_subject ON block_acl (subject_id);

