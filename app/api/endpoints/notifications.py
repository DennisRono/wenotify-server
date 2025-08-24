from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from wenotify.controllers.notifications import NotificationsController
from wenotify.dependencies.auth import GetCurrentUser
from wenotify.db.session import get_async_db
from wenotify.schemas.notifications import (
    NotificationResponse,
    NotificationUpdate,
    NotificationListResponse
)

notifications_router = APIRouter()
notifications_controller = NotificationsController()


@notifications_router.get("/", response_model=List[NotificationListResponse])
async def get_user_notifications(
    current_user: GetCurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
    db: AsyncSession = Depends(get_async_db),
):
    return await notifications_controller.get_user_notifications(skip, limit, unread_only, current_user, db)


@notifications_router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: UUID,
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await notifications_controller.get_notification(notification_id, current_user, db)


@notifications_router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: UUID,
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await notifications_controller.mark_notification_read(notification_id, current_user, db)


@notifications_router.patch("/mark-all-read", status_code=status.HTTP_200_OK)
async def mark_all_notifications_read(
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await notifications_controller.mark_all_notifications_read(current_user, db)


@notifications_router.delete("/{notification_id}", status_code=status.HTTP_200_OK)
async def delete_notification(
    notification_id: UUID,
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await notifications_controller.delete_notification(notification_id, current_user, db)
