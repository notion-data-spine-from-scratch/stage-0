# src/app/schemas.py

import uuid
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class BlockIn(BaseModel):
    parent_id: Optional[uuid.UUID] = None
    workspace_id: uuid.UUID
    type: str
    props: Dict[str, Any]


class BlockOut(BlockIn):
    id: uuid.UUID
    version: int


class BlockUpdate(BaseModel):
    props: Dict[str, Any]
    version: int = Field(
        ..., description="Expected current version for optimistic lock"
    )
