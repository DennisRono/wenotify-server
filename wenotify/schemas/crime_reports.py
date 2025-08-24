from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import ConfigDict, field_validator

from wenotify.schemas.base import (
    BaseSchemaCreate,
    BaseSchemaUpdate,
    BaseSchemaResponse,
)
from wenotify.enums import CrimeCategory, CrimeSeverity, ReportStatus


class CrimeReportBase(BaseSchemaCreate):
    """Base fields shared across crime report schemas."""
    model_config = ConfigDict(from_attributes=True)

    title: str
    description: str
    category: CrimeCategory
    severity: CrimeSeverity = CrimeSeverity.MEDIUM
    is_anonymous: bool = False
    is_emergency: bool = False

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Description cannot be empty")
        return v


class CrimeReportCreate(CrimeReportBase):
    """Schema for creating a new crime report."""
    location_id: UUID


class CrimeReportUpdate(BaseSchemaUpdate):
    """Schema for updating an existing crime report."""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[CrimeCategory] = None
    severity: Optional[CrimeSeverity] = None
    is_anonymous: Optional[bool] = None
    is_emergency: Optional[bool] = None
    priority_score: Optional[float] = None
    suspect_description: Optional[str] = None
    witness_count: Optional[int] = None
    estimated_loss: Optional[float] = None
    is_verified: Optional[bool] = None
    confidence_score: Optional[float] = None
    internal_notes: Optional[str] = None
    resolution_notes: Optional[str] = None
    assigned_officer_id: Optional[UUID] = None


class CrimeReportStatusUpdate(BaseSchemaUpdate):
    """Schema for updating the status of a report."""
    status: ReportStatus


class CrimeReportResponse(CrimeReportBase, BaseSchemaResponse):
    """Full schema for returning a crime report with metadata."""
    report_number: str
    reporter_id: UUID
    status: ReportStatus
    assigned_officer_id: Optional[UUID] = None
    location_id: UUID
    priority_score: Optional[float] = None
    suspect_description: Optional[str] = None
    witness_count: Optional[int] = None
    estimated_loss: Optional[float] = None
    is_verified: bool
    confidence_score: Optional[float] = None
    internal_notes: Optional[str] = None
    resolution_notes: Optional[str] = None


class CrimeReportListResponse(BaseSchemaResponse):
    """Lightweight schema for listing reports."""
    id: UUID
    report_number: str
    title: str
    category: CrimeCategory
    severity: CrimeSeverity
    status: ReportStatus
    is_emergency: bool
    created_at: datetime
