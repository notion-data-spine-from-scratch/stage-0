# src/app/models.py
import os

from sqlalchemy import MetaData, create_engine

from app.database import DATABASE_URL

# Derive a pure‐sync URL (so we don’t invoke any asyncpg calls at import time)
sync_url = DATABASE_URL
if sync_url.startswith("postgresql+asyncpg://"):
    sync_url = "postgresql://" + sync_url[len("postgresql+asyncpg://") :]
elif sync_url.startswith("postgres://"):
    # normalize the old postgres:// scheme
    sync_url = "postgresql://" + sync_url[len("postgres://") :]

# Create a synchronous engine for reflection
sync_engine = create_engine(sync_url, future=True)

# Global metadata object
metadata = MetaData()

# Reflect all tables from the existing database into metadata.tables
metadata.reflect(bind=sync_engine)
