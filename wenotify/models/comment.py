from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, Index, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from wenotify.models.base import Base, BaseMixin

if TYPE_CHECKING:
    from wenotify.models.user import User
    from wenotify.models.crime_report import CrimeReport


class Comment(Base, BaseMixin):
    """Comment model for updates and communication on crime reports."""
    
    __tablename__ = "comments"
    
    # References
    crime_report_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True
    )
    
    author_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True
    )
    
    # Content
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    # Visibility and Type
    is_internal: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    is_status_update: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    # Relationships
    crime_report: Mapped["CrimeReport"] = relationship(
        "CrimeReport",
        back_populates="comments",
        foreign_keys=[crime_report_id]
    )
    
    author: Mapped["User"] = relationship(
        "User",
        back_populates="comments",
        foreign_keys=[author_id]
    )
    
    # Constraints and Indexes
    __table_args__ = (
        Index('idx_comment_report_author', 'crime_report_id', 'author_id'),
        Index('idx_comment_internal_status', 'is_internal', 'is_status_update'),
    )
