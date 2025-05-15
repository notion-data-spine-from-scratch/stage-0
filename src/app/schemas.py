from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import ConfigDict  # Pydantic v2
from pydantic import BaseModel, Field


class BlockIn(BaseModel):
    parent_id: Optional[UUID]
    workspace_id: UUID
    type_: str = Field(..., alias="type")  # JSON key "type" → python attr "type_"
    props: Dict[str, Any]

    model_config = ConfigDict(populate_by_name=True)


class BlockUpdate(BaseModel):
    props: Dict[str, Any]
    version: int


class BlockOut(BlockIn):
    id: UUID
    version: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
