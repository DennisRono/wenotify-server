from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from wenotify.models.base import Base, BaseMixin
from wenotify.enums import NotificationStatus, NotificationType

if TYPE_CHECKING:
    from wenotify.models.user import User
    from wenotify.models.crime_report import CrimeReport


class Notification(Base, BaseMixin):
    """Notification model for system alerts and updates."""
    
    __tablename__ = "notifications"
    
    # Recipient
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Related Crime Report (optional)
    crime_report_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("crime_reports.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    
    # Notification Details
    notification_type: Mapped[NotificationType] = mapped_column(
        nullable=False,
        index=True
    )
    
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    # Status and Delivery
    status: Mapped[NotificationStatus] = mapped_column(
        nullable=False,
        index=True,
        default=NotificationStatus.SENT
    )
    
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    # Delivery Channels
    sent_via_email: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    sent_via_sms: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    sent_via_push: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    
    # Priority and Urgency
    is_urgent: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="notifications",
        foreign_keys=[user_id]
    )
    
    crime_report: Mapped["CrimeReport | None"] = relationship(
        "CrimeReport",
        back_populates="notifications",
        foreign_keys=[crime_report_id]
    )
    
    # Constraints and Indexes
    __table_args__ = (
        Index('idx_notification_user_status', 'user_id', 'status'),
        Index('idx_notification_type_urgent', 'notification_type', 'is_urgent'),
        Index('idx_notification_read_status', 'is_read', 'status'),
        Index('idx_notification_report_type', 'crime_report_id', 'notification_type'),
    )
