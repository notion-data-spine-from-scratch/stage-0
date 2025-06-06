import pytest
fakeredis_aioredis = pytest.importorskip("fakeredis.aioredis")

from app.cache import cache_get, cache_set


@pytest.fixture(autouse=True)
async def fake_redis(monkeypatch):
    redis = fakeredis_aioredis.FakeRedis()

    async def _get_redis():
        return redis

    monkeypatch.setattr("app.cache.get_redis", _get_redis)
    yield redis


@pytest.mark.asyncio
async def test_cache_roundtrip():
    await cache_set("foo", {"bar": 1})
    assert await cache_get("foo") == {"bar": 1}

    # delete using ttl=0
    await cache_set("foo", None, ttl=0)
    assert await cache_get("foo") is None
