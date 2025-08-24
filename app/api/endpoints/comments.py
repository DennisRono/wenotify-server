from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from wenotify.controllers.comments import CommentsController
from wenotify.dependencies.auth import GetCurrentUser
from wenotify.db.session import get_async_db
from wenotify.schemas.comments import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
    CommentListResponse
)

comments_router = APIRouter()
comments_controller = CommentsController()


@comments_router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_data: CommentCreate,
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await comments_controller.create_comment(comment_data, current_user, db)


@comments_router.get("/report/{report_id}", response_model=List[CommentListResponse])
async def get_report_comments(
    report_id: UUID,
    current_user: GetCurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db),
):
    return await comments_controller.get_report_comments(report_id, skip, limit, current_user, db)


@comments_router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: UUID,
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await comments_controller.get_comment(comment_id, current_user, db)


@comments_router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: UUID,
    comment_data: CommentUpdate,
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await comments_controller.update_comment(comment_id, comment_data, current_user, db)


@comments_router.delete("/{comment_id}", status_code=status.HTTP_200_OK)
async def delete_comment(
    comment_id: UUID,
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await comments_controller.delete_comment(comment_id, current_user, db)
