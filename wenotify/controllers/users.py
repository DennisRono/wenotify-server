from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select, update
from sqlalchemy.orm import selectinload
from wenotify.dependencies.auth import create_access_token, create_refresh_token
from wenotify.schemas.users import LoginRequest, LoginResponse, UserCreate, UserResponse, UserUpdate, PasswordChangeRequest
from wenotify.models.user import User
from wenotify.enums import UserRole, UserStatus
from fastapi import HTTPException, status
from passlib.context import CryptContext
from uuid import uuid4
from datetime import datetime, timezone
from wenotify.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UsersController:
    async def register_user(self, user_data: UserCreate, db: AsyncSession):
        # Check if user already exists
        stmt = select(User).where(User.email == user_data.email)
        existing_user = await db.scalar(stmt)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Hash password
        hashed_password = pwd_context.hash(user_data.password)
        
        # Create new user
        new_user = User(
            id=uuid4(),
            email=user_data.email,
            phone_number=user_data.phone_number,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            password_hash=hashed_password,
            role=user_data.role or UserRole.CITIZEN,
            status=UserStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    
    async def get_user_profile(self, current_user, db: AsyncSession):
        stmt = select(User).where(User.id == current_user.user_id)
        user = await db.scalar(stmt)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    async def update_user_profile(self, user_data: UserUpdate, current_user, db: AsyncSession):
        stmt = select(User).where(User.id == current_user.user_id)
        user = await db.scalar(stmt)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields if provided
        update_data = user_data.model_dump(exclude_unset=True)
        if update_data:
            update_data['updated_at'] = datetime.now(timezone.utc)
            update_data['updated_by_id'] = current_user.user_id
            
            stmt = update(User).where(User.id == current_user.user_id).values(**update_data)
            await db.execute(stmt)
            await db.commit()
            await db.refresh(user)
        
        return user
    
    async def change_password(self, password_data: PasswordChangeRequest, current_user, db: AsyncSession):
        stmt = select(User).where(User.id == current_user.user_id)
        user = await db.scalar(stmt)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not pwd_context.verify(password_data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Hash new password
        new_password_hash = pwd_context.hash(password_data.new_password)
        
        # Update password
        stmt = update(User).where(User.id == current_user.user_id).values(
            password_hash=new_password_hash,
            updated_at=datetime.now(timezone.utc),
            updated_by_id=current_user.user_id
        )
        await db.execute(stmt)
        await db.commit()
        
        return {"message": "Password updated successfully"}
    
    async def deactivate_account(self, current_user, db: AsyncSession):
        stmt = update(User).where(User.id == current_user.user_id).values(
            status=UserStatus.INACTIVE,
            deleted_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            updated_by_id=current_user.user_id
        )
        await db.execute(stmt)
        await db.commit()
        
        return {"message": "Account deactivated successfully"}

    async def authenticate_user(self, login_data: LoginRequest, db: AsyncSession) -> LoginResponse:
        email = login_data.email.strip().lower()

        stmt = select(User).where(
            and_(
                User.email == email,
                User.is_active == True,
            )
        )
        result = await db.scalars(stmt)
        user = result.first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password
        if not pwd_context.verify(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.phone_number,
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
            "status": user.status.value if hasattr(user.status, "value") else str(user.status),
            "is_verified": user.is_verified,
        }

        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return LoginResponse(
            user=UserResponse.model_validate(user),
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    
    