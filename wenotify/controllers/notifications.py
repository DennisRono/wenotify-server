from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from sqlalchemy.orm import joinedload
from wenotify.models.notification import Notification
from wenotify.enums import NotificationStatus
from fastapi import HTTPException, status
from uuid import UUID
from datetime import datetime, timezone

class NotificationsController:
    async def get_user_notifications(self, skip: int, limit: int, unread_only: bool, current_user, db: AsyncSession):
        # Build query
        conditions = [Notification.user_id == current_user.user_id]
        
        if unread_only:
            conditions.append(Notification.status == NotificationStatus.UNREAD)
        
        stmt = select(Notification).where(
            and_(*conditions)
        ).offset(skip).limit(limit).order_by(Notification.created_at.desc())
        
        result = await db.execute(stmt)
        notifications = result.scalars().all()
        return notifications
    
    async def get_notification(self, notification_id: UUID, current_user, db: AsyncSession):
        stmt = select(Notification).where(Notification.id == notification_id)
        notification = await db.scalar(stmt)
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Access control - users can only view their own notifications
        if notification.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own notifications"
            )
        
        return notification
    
    async def mark_notification_read(self, notification_id: UUID, current_user, db: AsyncSession):
        stmt = select(Notification).where(Notification.id == notification_id)
        notification = await db.scalar(stmt)
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Access control
        if notification.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own notifications"
            )
        
        # Mark as read
        stmt = update(Notification).where(Notification.id == notification_id).values(
            status=NotificationStatus.READ,
            read_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            updated_by_id=current_user.user_id
        )
        await db.execute(stmt)
        await db.commit()
        await db.refresh(notification)
        
        return notification
    
    async def mark_all_notifications_read(self, current_user, db: AsyncSession):
        stmt = update(Notification).where(
            and_(
                Notification.user_id == current_user.user_id,
                Notification.status == NotificationStatus.UNREAD
            )
        ).values(
            status=NotificationStatus.READ,
            read_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            updated_by_id=current_user.user_id
        )
        
        result = await db.execute(stmt)
        await db.commit()
        
        return {"message": f"Marked {result.rowcount} notifications as read"}
    
    async def delete_notification(self, notification_id: UUID, current_user, db: AsyncSession):
        stmt = select(Notification).where(Notification.id == notification_id)
        notification = await db.scalar(stmt)
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Access control
        if notification.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own notifications"
            )
        
        # Soft delete
        stmt = update(Notification).where(Notification.id == notification_id).values(
            deleted_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            updated_by_id=current_user.user_id
        )
        await db.execute(stmt)
        await db.commit()
        
        return {"message": "Notification deleted successfully"}
