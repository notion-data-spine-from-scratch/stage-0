from typing import List
import os
import uuid

from fastapi import APIRouter, Depends
from meilisearch import Client
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import get_db
from app.dependencies import get_current_user, User

router = APIRouter(prefix="/search")

MEILI_URL = os.getenv("MEILI_URL", "http://localhost:7700")
MEILI_KEY = os.getenv("MEILI_MASTER_KEY", "masterKey")

client = Client(MEILI_URL, MEILI_KEY)
index = client.index("blocks")

async def _allowed_block_ids(user_id: uuid.UUID, db: AsyncSession) -> set[uuid.UUID]:
    q = """
        SELECT b.id
          FROM blocks b
          JOIN block_acl a ON a.block_id = b.id
         WHERE a.subject_id = :uid
    """
    rows = await db.execute(text(q), {"uid": user_id})
    return {r[0] for r in rows.all()}

@router.get("/")
async def search(
    q: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    results = index.search(q).get("hits", [])
    allowed = await _allowed_block_ids(uuid.UUID(user.id), db)
    filtered = [r for r in results if uuid.UUID(r["id"]) in allowed]
    return filtered
