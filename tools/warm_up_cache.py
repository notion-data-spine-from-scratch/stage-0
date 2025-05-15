import asyncio
import os
import random

import asyncpg
import httpx
from httpx import ReadTimeout
from tqdm import tqdm

API = os.getenv("API_URL", "http://localhost:8000")

DB_DSN = os.getenv(
    "DB_DSN",
    "postgresql://notion:notion@localhost:5433/notion",
)


async def main(n: int = 10_000, workers: int = 50):
    print(f"Connecting to {DB_DSN}…")
    pool = await asyncpg.create_pool(DB_DSN, min_size=2, max_size=4)
    async with pool.acquire() as con:
        records = await con.fetch("SELECT id FROM blocks LIMIT 100000")
        ids = [r["id"] for r in records]
    print(f"Loaded {len(ids)} block IDs.")

    sem = asyncio.Semaphore(workers)
    async with httpx.AsyncClient(timeout=10.0) as client:

        async def one():
            blk = random.choice(ids)
            async with sem:
                try:
                    await client.get(f"{API}/blocks/{blk}")
                except ReadTimeout:
                    pass  # ignore timeouts

        # schedule all tasks
        tasks = [one() for _ in range(n)]

        # as each task completes, update progress bar
        for _ in tqdm(
            asyncio.as_completed(tasks),
            total=n,
            desc="Warming cache",
            mininterval=0.5,
        ):
            try:
                await _
            except Exception:
                # ignore any other errors
                pass

    print("Warm‑up complete.")


if __name__ == "__main__":
    import fire

    # allow `python warm_up_cache.py --n 2000 --workers 20`
    fire.Fire(main)
