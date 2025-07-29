import os
import json
from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from sqlalchemy import text

router = APIRouter(prefix="/billing")

@router.post("/webhook")
async def webhook(req: Request, db: AsyncSession = Depends(get_db)):
    payload = await req.body()
    event = json.loads(payload)
    workspace = event.get("data", {}).get("object", {}).get("metadata", {}).get("workspace_id")
    plan_id = event.get("data", {}).get("object", {}).get("plan_id")
    if workspace and plan_id:
        await db.execute(
            text("UPDATE workspace_plans SET plan_id=:p WHERE workspace_id=:w"),
            {"p": plan_id, "w": workspace},
        )
        await db.commit()
    return {"status": "ok"}
