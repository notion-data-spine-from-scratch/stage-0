import asyncio

import pytest
from sqlalchemy import text

from app.database import engine, get_db


@pytest.mark.asyncio
async def test_can_connect_and_query():
    # verify engine can connect
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1

    # verify session dependency works
    # mimic FastAPI dependency call
    gen = get_db()
    session = await gen.__anext__()  # get the session
    scalar = await session.execute(text("SELECT 1"))
    assert scalar.scalar() == 1
    await gen.aclose()
