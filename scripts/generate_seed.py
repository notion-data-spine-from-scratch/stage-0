#!/usr/bin/env python3
"""
scripts/generate_seed.py

Generate realistic seed data:
  - N users
  - M workspaces per user
  - K total blocks (evenly distributed, with remainder spread)
Usage:
  DSN environment variable overrides default.
  poetry run python scripts/generate_seed.py --users 10 --workspaces 5 --blocks 100000
"""
import asyncio
import json
import os
import uuid
from typing import List, Optional, Tuple

import asyncpg
import fire

# Read DSN from environment or use default Compose network address
DSN = os.getenv("DSN", "postgres://notion:notion@db:5432/notion")


async def generate(users: int = 10, workspaces: int = 5, blocks: int = 100_000):
    # Connect to Postgres
    conn = await asyncpg.connect(DSN)

    # 1. Wipe existing data
    await conn.execute(
        """
        TRUNCATE block_acl, blocks, workspace_plans, plans, workspaces, users
        RESTART IDENTITY CASCADE;
    """
    )

    # 2. Create users
    user_ids = [uuid.uuid4() for _ in range(users)]
    user_rows = [
        (u, f"user{idx}@example.com", "hashed_password")
        for idx, u in enumerate(user_ids)
    ]
    await conn.executemany(
        "INSERT INTO users (id, email, hashed_password) VALUES ($1, $2, $3)", user_rows
    )

    # 3. Create workspaces
    ws_ids = []
    for u in user_ids:
        for i in range(workspaces):
            wid = uuid.uuid4()
            ws_ids.append(wid)
            await conn.execute(
                "INSERT INTO workspaces (id, owner_id, name) VALUES ($1, $2, $3)",
                wid,
                u,
                f"WS-{u.hex[:6]}-{i}",
            )

    # 4. Seed plans & assign Free plan (id=1)
    await conn.execute(
        """
        INSERT INTO plans (name, max_blocks, price_cents) VALUES
          ('Free', 10000, 0),
          ('Team', 100000, 999),
          ('Enterprise', 100000000, 9999)
        ON CONFLICT DO NOTHING;
    """
    )
    await conn.executemany(
        "INSERT INTO workspace_plans (workspace_id, plan_id) VALUES ($1, 1)",
        [(w,) for w in ws_ids],
    )

    # 5. Bulk-generate blocks with even distribution + remainder
    batch: List[Tuple[uuid.UUID, Optional[uuid.UUID], uuid.UUID, str, str, int]] = []
    total_ws = len(ws_ids)
    base, rem = divmod(blocks, total_ws)
    for idx, w in enumerate(ws_ids):
        parent = None
        count = base + (1 if idx < rem else 0)
        for n in range(count):
            bid = uuid.uuid4()
            props = {"text": f"Block {n} in {w.hex[:6]}"}
            batch.append((bid, parent, w, "text", json.dumps(props), 1))
            parent = bid

            # flush every 1000 records
            if len(batch) >= 1000:
                await conn.copy_records_to_table(
                    "blocks",
                    records=batch,
                    columns=[
                        "id",
                        "parent_id",
                        "workspace_id",
                        "type",
                        "props",
                        "version",
                    ],
                )
                batch.clear()

    # Flush any remainder
    if batch:
        await conn.copy_records_to_table(
            "blocks",
            records=batch,
            columns=["id", "parent_id", "workspace_id", "type", "props", "version"],
        )

    print(f"Seeded {users} users, {len(ws_ids)} workspaces, ~{blocks} blocks.")
    await conn.close()


def main(users: int = 10, workspaces: int = 5, blocks: int = 100_000):
    asyncio.run(generate(users, workspaces, blocks))


if __name__ == "__main__":
    fire.Fire(main)
