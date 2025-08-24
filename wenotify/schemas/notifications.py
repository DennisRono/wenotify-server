from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import ConfigDict

from wenotify.schemas.base import (
    BaseSchemaCreate,
    BaseSchemaUpdate,
    BaseSchemaResponse,
)
from wenotify.enums import NotificationStatus, NotificationType


class NotificationBase(BaseSchemaCreate):
    """Base fields shared across notification schemas."""
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    crime_report_id: Optional[UUID] = None
    notification_type: NotificationType
    title: str
    message: str
    status: NotificationStatus = NotificationStatus.SENT
    is_read: bool = False
    sent_via_email: bool = False
    sent_via_sms: bool = False
    sent_via_push: bool = True
    is_urgent: bool = False


class NotificationUpdate(BaseSchemaUpdate):
    """Schema for updating notification status."""
    is_read: Optional[bool] = None
    status: Optional[NotificationStatus] = None
    sent_via_email: Optional[bool] = None
    sent_via_sms: Optional[bool] = None
    sent_via_push: Optional[bool] = None
    is_urgent: Optional[bool] = None


class NotificationResponse(NotificationBase, BaseSchemaResponse):
    """Full schema for returning a notification with metadata."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    created_by_id: Optional[UUID] = None
    updated_by_id: Optional[UUID] = None


class NotificationListResponse(BaseSchemaResponse):
    """Lightweight schema for listing user notifications."""
    id: UUID
    title: str
    message: str
    notification_type: NotificationType
    status: NotificationStatus
    is_read: bool
    is_urgent: bool
    created_at: datetime
