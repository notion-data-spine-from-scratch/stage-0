import os

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Read DATABASE_URL from env, defaulting to our Compose URL
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://notion:notion@db:5432/notion"
)

# 1. Create the async engine
engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

# 2. Create a configured "sessionmaker"
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


# 3. Dependency to yield a session per request
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
