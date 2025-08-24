from sqlalchemy.ext.asyncio import AsyncSession
from wenotify.schemas.users import UserCreate, UserUpdate, PasswordChangeRequest


class UsersController:
    async def register_user(self, user_data: UserCreate, db: AsyncSession):
        pass
    
    async def get_user_profile(self, current_user, db: AsyncSession):
        pass
    
    async def update_user_profile(self, user_data: UserUpdate, current_user, db: AsyncSession):
        pass
    
    async def change_password(self, password_data: PasswordChangeRequest, current_user, db: AsyncSession):
        pass
    
    async def deactivate_account(self, current_user, db: AsyncSession):
        pass
