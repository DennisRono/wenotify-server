from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class BaseSchemaCreate(BaseModel):
    """Base schema for creation requests."""
    model_config = ConfigDict(from_attributes=True)


class BaseSchemaUpdate(BaseModel):
    """Base schema for update requests."""
    model_config = ConfigDict(from_attributes=True)


class BaseSchemaResponse(BaseModel):
    """Base schema for responses including audit fields."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    created_by_id: Optional[UUID] = None
    updated_by_id: Optional[UUID] = None
