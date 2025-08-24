from sqlalchemy.ext.asyncio import AsyncSession
from wenotify.schemas.comments import CommentCreate, CommentUpdate
from uuid import UUID


class CommentsController:
    async def create_comment(self, comment_data: CommentCreate, current_user, db: AsyncSession):
        pass
    
    async def get_report_comments(self, report_id: UUID, skip: int, limit: int, current_user, db: AsyncSession):
        pass
    
    async def get_comment(self, comment_id: UUID, current_user, db: AsyncSession):
        pass
    
    async def update_comment(self, comment_id: UUID, comment_data: CommentUpdate, current_user, db: AsyncSession):
        pass
    
    async def delete_comment(self, comment_id: UUID, current_user, db: AsyncSession):
        pass
