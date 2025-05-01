# src/app/schemas.py

from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BlockIn(BaseModel):
    parent_id: Optional[UUID]
    workspace_id: UUID
    type: str
    props: Dict[str, Any]


class BlockUpdate(BaseModel):
    props: Dict[str, Any]
    version: int


class BlockOut(BaseModel):
    id: UUID
    parent_id: Optional[UUID]
    workspace_id: UUID
    type: str
    props: Dict[str, Any]
    version: int

    # replace orm_mode = True with the new from_attributes flag
    model_config = ConfigDict(from_attributes=True)
