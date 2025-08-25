from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from sqlalchemy.orm import joinedload
from wenotify.schemas.comments import CommentCreate, CommentUpdate
from wenotify.models.comment import Comment
from wenotify.models.crime_report import CrimeReport
from wenotify.enums import UserRole
from fastapi import HTTPException, status
from uuid import UUID, uuid4
from datetime import datetime, timezone

class CommentsController:
    async def create_comment(self, comment_data: CommentCreate, current_user, db: AsyncSession):
        # Verify report exists and user has access
        report_stmt = select(CrimeReport).where(CrimeReport.id == comment_data.crime_report_id)
        report = await db.scalar(report_stmt)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crime report not found"
            )
        
        # Access control - citizens can only comment on their own reports or public ones
        if (current_user.role == UserRole.CITIZEN and 
            report.reporter_id != current_user.user_id and 
            report.is_anonymous):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot comment on this report"
            )
        
        # Create comment
        new_comment = Comment(
            id=uuid4(),
            crime_report_id=comment_data.crime_report_id,
            content=comment_data.content,
            author_id=current_user.user_id,
            is_internal=comment_data.is_internal or False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            created_by_id=current_user.user_id
        )
        
        db.add(new_comment)
        await db.commit()
        await db.refresh(new_comment)
        return new_comment
    
    async def get_report_comments(self, report_id: UUID, skip: int, limit: int, current_user, db: AsyncSession):
        # Verify report access
        report_stmt = select(CrimeReport).where(CrimeReport.id == report_id)
        report = await db.scalar(report_stmt)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crime report not found"
            )
        
        # Access control
        if (current_user.role == UserRole.CITIZEN and 
            report.reporter_id != current_user.user_id and 
            report.is_anonymous):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Build query
        stmt = select(Comment).options(
            joinedload(Comment.author)
        ).where(
            and_(
                Comment.crime_report_id == report_id,
                Comment.deleted_at.is_(None)
            )
        )
        
        # Filter internal comments for citizens
        if current_user.role == UserRole.CITIZEN:
            stmt = stmt.where(Comment.is_internal == False)
        
        # Apply pagination and ordering
        stmt = stmt.offset(skip).limit(limit).order_by(Comment.created_at.asc())
        
        result = await db.execute(stmt)
        comments = result.scalars().all()
        return comments
    
    async def get_comment(self, comment_id: UUID, current_user, db: AsyncSession):
        stmt = select(Comment).options(
            joinedload(Comment.author),
            joinedload(Comment.crime_report)
        ).where(Comment.id == comment_id)
        
        comment = await db.scalar(stmt)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Access control
        if (current_user.role == UserRole.CITIZEN and 
            comment.crime_report.reporter_id != current_user.user_id and 
            comment.is_internal):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return comment
    
    async def update_comment(self, comment_id: UUID, comment_data: CommentUpdate, current_user, db: AsyncSession):
        stmt = select(Comment).where(Comment.id == comment_id)
        comment = await db.scalar(stmt)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Permission check - only author can update
        if comment.author_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own comments"
            )
        
        # Update comment
        update_data = comment_data.model_dump(exclude_unset=True)
        if update_data:
            update_data['updated_at'] = datetime.now(timezone.utc)
            update_data['updated_by_id'] = current_user.user_id
            
            stmt = update(Comment).where(Comment.id == comment_id).values(**update_data)
            await db.execute(stmt)
            await db.commit()
            await db.refresh(comment)
        
        return comment
    
    async def delete_comment(self, comment_id: UUID, current_user, db: AsyncSession):
        stmt = select(Comment).where(Comment.id == comment_id)
        comment = await db.scalar(stmt)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Permission check - author or admin can delete
        if (comment.author_id != current_user.user_id and 
            current_user.role != UserRole.ADMIN):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own comments"
            )
        
        # Soft delete
        stmt = update(Comment).where(Comment.id == comment_id).values(
            deleted_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            updated_by_id=current_user.user_id
        )
        await db.execute(stmt)
        await db.commit()
        
        return {"message": "Comment deleted successfully"}
