from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import ConfigDict, field_validator

from wenotify.schemas.base import (
    BaseSchemaCreate,
    BaseSchemaUpdate,
    BaseSchemaResponse,
)


class CommentBase(BaseSchemaCreate):
    """Base fields shared across comment schemas."""
    model_config = ConfigDict(from_attributes=True)

    content: str
    is_internal: bool = False
    is_status_update: bool = False

    @field_validator("content")
    @classmethod
    def validate_content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Comment content cannot be empty")
        return v


class CommentCreate(CommentBase):
    """Schema for creating a new comment."""
    crime_report_id: UUID


class CommentUpdate(BaseSchemaUpdate):
    """Schema for updating an existing comment."""
    content: Optional[str] = None
    is_internal: Optional[bool] = None
    is_status_update: Optional[bool] = None


class CommentResponse(CommentBase, BaseSchemaResponse):
    """Full schema for returning a single comment with metadata."""
    crime_report_id: UUID
    author_id: UUID


class CommentListResponse(BaseSchemaResponse):
    """Schema for listing comments under a report."""
    id: UUID
    content: str
    author_id: UUID
    created_at: datetime
