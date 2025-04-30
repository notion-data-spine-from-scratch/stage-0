import os

from sqlalchemy import MetaData, create_engine

# Grab the same DATABASE_URL, but drop the "+asyncpg" suffix for a sync driver
from app.database import DATABASE_URL

SYNC_DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")

# Create a true synchronous Engine (psycopg2 under the hood)
sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)

# Reflect into this metadata
metadata = MetaData()
metadata.reflect(bind=sync_engine)
