from typing import TYPE_CHECKING, List
from uuid import UUID

from sqlalchemy import Boolean, Float, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from wenotify.models.base import Base, BaseMixin
from wenotify.enums import CrimeCategory, CrimeSeverity, ReportStatus

if TYPE_CHECKING:
    from wenotify.models.user import User
    from wenotify.models.location import Location
    from wenotify.models.evidence import Evidence
    from wenotify.models.comment import Comment
    from wenotify.models.notification import Notification


class CrimeReport(Base, BaseMixin):
    """Crime report model for storing incident reports."""
    
    __tablename__ = "crime_reports"
    
    # Report Identification
    report_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Reporter Information
    reporter_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True
    )
    
    is_anonymous: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    # Crime Details
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True
    )
    
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    category: Mapped[CrimeCategory] = mapped_column(
        nullable=False,
        index=True
    )
    
    severity: Mapped[CrimeSeverity] = mapped_column(
        nullable=False,
        index=True,
        default=CrimeSeverity.MEDIUM
    )
    
    # Status and Assignment
    status: Mapped[ReportStatus] = mapped_column(
        nullable=False,
        index=True,
        default=ReportStatus.SUBMITTED
    )
    
    assigned_officer_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        index=True
    )
    
    # Location Information
    location_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True
    )
    
    # Emergency and Priority
    is_emergency: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    priority_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        index=True
    )
    
    # Additional Information
    suspect_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    witness_count: Mapped[int | None] = mapped_column(
        nullable=True
    )
    
    estimated_loss: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )
    
    # Verification and Quality
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    confidence_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )
    
    # Internal Notes
    internal_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    resolution_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    # Relationships
    reporter: Mapped["User"] = relationship(
        "User",
        back_populates="submitted_reports",
        foreign_keys=[reporter_id]
    )
    
    assigned_officer: Mapped["User | None"] = relationship(
        "User",
        back_populates="assigned_reports",
        foreign_keys=[assigned_officer_id]
    )
    
    location: Mapped["Location"] = relationship(
        "Location",
        back_populates="crime_reports",
        foreign_keys=[location_id]
    )
    
    evidence: Mapped[List["Evidence"]] = relationship(
        "Evidence",
        back_populates="crime_report",
        foreign_keys="Evidence.crime_report_id",
        cascade="all, delete-orphan"
    )
    
    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="crime_report",
        foreign_keys="Comment.crime_report_id",
        cascade="all, delete-orphan"
    )
    
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="crime_report",
        foreign_keys="Notification.crime_report_id",
        cascade="all, delete-orphan"
    )
    
    # Constraints and Indexes
    __table_args__ = (
        Index('idx_crime_report_status_category', 'status', 'category'),
        Index('idx_crime_report_severity_emergency', 'severity', 'is_emergency'),
        Index('idx_crime_report_location_category', 'location_id', 'category'),
        Index('idx_crime_report_reporter_status', 'reporter_id', 'status'),
        Index('idx_crime_report_assigned_status', 'assigned_officer_id', 'status'),
        Index('idx_crime_report_priority', 'priority_score', 'is_emergency'),
        Index('idx_crime_report_verification', 'is_verified', 'status'),
    )
