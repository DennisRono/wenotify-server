from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import ConfigDict, field_validator

from wenotify.schemas.base import (
    BaseSchemaCreate,
    BaseSchemaUpdate,
    BaseSchemaResponse,
)
from wenotify.enums import EvidenceType


class EvidenceBase(BaseSchemaCreate):
    """Base fields shared across evidence schemas."""
    model_config = ConfigDict(from_attributes=True)

    evidence_type: EvidenceType
    description: Optional[str] = None

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Description cannot be empty string")
        return v


class EvidenceUpdate(BaseSchemaUpdate):
    """Schema for updating evidence details."""
    description: Optional[str] = None
    processing_notes: Optional[str] = None
    is_processed: Optional[bool] = None


class EvidenceResponse(EvidenceBase, BaseSchemaResponse):
    """Full schema for returning a single piece of evidence."""
    crime_report_id: UUID
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    file_hash: str
    is_encrypted: bool
    chain_of_custody: Optional[str] = None
    is_processed: bool
    processing_notes: Optional[str] = None


class EvidenceListResponse(BaseSchemaResponse):
    """Lightweight schema for listing evidence under a report."""
    id: UUID
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    evidence_type: EvidenceType
    is_processed: bool
    created_at: datetime
