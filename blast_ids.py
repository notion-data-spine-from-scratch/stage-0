import asyncio
import os
import sys
import time

import aiohttp
from tqdm import tqdm

# Usage: python blast_ids.py all_ids.txt
API = os.getenv("API_URL", "http://localhost:8000")
CONCURRENCY = 200  # adjust based on your machine's capability


async def hit(session, url, sem):
    async with sem:
        try:
            async with session.get(url) as resp:
                await resp.read()
        except Exception:
            pass  # ignore timeouts or connection errors


async def main(ids_file):
    # load block URLs
    ids = [line.strip() for line in open(ids_file) if line.strip()]
    urls = [f"{API}/blocks/{bid}" for bid in ids]
    print(f"Loaded {len(urls):,} URLs to blast.")

    sem = asyncio.Semaphore(CONCURRENCY)
    timeout = aiohttp.ClientTimeout(total=10)
    connector = aiohttp.TCPConnector(limit=CONCURRENCY)

    t0 = time.perf_counter()
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        # schedule all tasks but let semaphore throttle concurrency
        tasks = [hit(session, url, sem) for url in urls]
        # use as_completed to update progress as each finishes
        for coro in tqdm(
            asyncio.as_completed(tasks), total=len(tasks), desc="Blasting IDs"
        ):
            await coro
    dt = time.perf_counter() - t0
    print(f"Done {len(urls):,} calls in {dt:.1f}s → {len(urls)/dt:,.0f} req/s")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python blast_ids.py all_ids.txt")
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
