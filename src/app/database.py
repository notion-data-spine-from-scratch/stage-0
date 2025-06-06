import os

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# read env or fallback
_raw_url = os.getenv(
    "DATABASE_URL",
    "postgresql://notion:notion@db:5432/notion",  # fallback *without* driver
)

# Normalize legacy postgres:// scheme and ensure +asyncpg driver
if _raw_url.startswith("postgres://"):
    _raw_url = "postgresql://" + _raw_url[len("postgres://") :]

if _raw_url.startswith("postgresql://"):
    DATABASE_URL = _raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    DATABASE_URL = _raw_url  # already has +asyncpg or other driver

engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,
    poolclass=NullPool,
    future=True,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
