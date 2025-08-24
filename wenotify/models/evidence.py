from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import BigInteger, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from wenotify.models.base import Base, BaseMixin
from wenotify.enums import EvidenceType

if TYPE_CHECKING:
    from wenotify.models.crime_report import CrimeReport


class Evidence(Base, BaseMixin):
    """Evidence model for storing files and media related to crime reports."""
    
    __tablename__ = "evidence"
    
    # Crime Report Reference
    crime_report_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True
    )
    
    # File Information
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    
    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )
    
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    
    # Evidence Classification
    evidence_type: Mapped[EvidenceType] = mapped_column(
        nullable=False,
        index=True
    )
    
    # Metadata
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    # Security and Integrity
    file_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True
    )
    
    is_encrypted: Mapped[bool] = mapped_column(
        default=True,
        nullable=False
    )
    
    # Chain of Custody
    chain_of_custody: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    # Processing Status
    is_processed: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        index=True
    )
    
    processing_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    # Relationships
    crime_report: Mapped["CrimeReport"] = relationship(
        "CrimeReport",
        back_populates="evidence",
        foreign_keys=[crime_report_id]
    )
    
    # Constraints and Indexes
    __table_args__ = (
        Index('idx_evidence_report_type', 'crime_report_id', 'evidence_type'),
        Index('idx_evidence_hash_type', 'file_hash', 'evidence_type'),
        Index('idx_evidence_processing', 'is_processed', 'evidence_type'),
    )
