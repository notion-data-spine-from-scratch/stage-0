import json
import os
from typing import Any, Optional

import redis.asyncio as aioredis  # redis-py’s asyncio client

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
_redis: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    return _redis


async def cache_get(key: str) -> Optional[Any]:
    try:
        r = await get_redis()
        data = await r.get(key)
        if data is not None:
            return json.loads(data)
    except Exception:
        # swallow connectivity or parse errors
        pass
    return None


async def cache_set(key: str, value: Any, ttl: int = 60) -> None:
    try:
        r = await get_redis()
        # if ttl <= 0, delete
        if ttl <= 0:
            await r.delete(key)
        else:
            await r.set(key, json.dumps(value), ex=ttl)
    except Exception:
        # ignore any Redis errors
        pass
