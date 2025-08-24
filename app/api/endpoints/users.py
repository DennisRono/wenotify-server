from fastapi import APIRouter, Depends, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from wenotify.controllers.users import UsersController
from wenotify.dependencies.auth import GetCurrentUser
from wenotify.db.session import get_async_db
from wenotify.schemas.users import (
    LoginRequest,
    UserCreate,
    UserResponse,
    UserUpdate,
    UserProfileResponse,
    PasswordChangeRequest
)

users_router = APIRouter()
users_controller = UsersController()

@users_router.post("/auth/login")
async def authenticate_user(
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_async_db),
):
    login_data = LoginRequest(email=username, password=password)
    return await users_controller.authenticate_user(login_data=login_data, db=db)


@users_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_async_db),
):
    return await users_controller.register_user(user_data, db)


@users_router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await users_controller.get_user_profile(current_user, db)


@users_router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_data: UserUpdate,
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await users_controller.update_user_profile(user_data, current_user, db)


@users_router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await users_controller.change_password(password_data, current_user, db)


@users_router.delete("/deactivate", status_code=status.HTTP_200_OK)
async def deactivate_account(
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_async_db),
):
    return await users_controller.deactivate_account(current_user, db)
