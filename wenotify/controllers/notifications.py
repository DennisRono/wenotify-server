from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID


class NotificationsController:
    async def get_user_notifications(self, skip: int, limit: int, unread_only: bool, current_user, db: AsyncSession):
        pass
    
    async def get_notification(self, notification_id: UUID, current_user, db: AsyncSession):
        pass
    
    async def mark_notification_read(self, notification_id: UUID, current_user, db: AsyncSession):
        pass
    
    async def mark_all_notifications_read(self, current_user, db: AsyncSession):
        pass
    
    async def delete_notification(self, notification_id: UUID, current_user, db: AsyncSession):
        pass
