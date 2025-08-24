from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, HttpUrl, constr, ConfigDict

from wenotify.schemas.base import (
    BaseSchemaCreate,
    BaseSchemaUpdate,
    BaseSchemaResponse,
)
from wenotify.enums import UserRole, UserStatus


class UserBase(BaseSchemaCreate):
    """Base fields shared across user schemas."""

    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    phone_number: Optional[str] = Field(None, min_length=7, max_length=20)
    first_name: str
    last_name: str
    role: UserRole = UserRole.CITIZEN
    status: UserStatus = UserStatus.PENDING_VERIFICATION
    profile_picture_url: Optional[HttpUrl] = None
    bio: Optional[str] = None
    badge_number: Optional[str] = None
    department: Optional[str] = None
    rank: Optional[str] = None
    county: Optional[str] = None
    sub_county: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseSchemaUpdate):
    """Schema for updating user profile."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = Field(None, min_length=7, max_length=20)
    profile_picture_url: Optional[HttpUrl] = None
    bio: Optional[str] = None
    department: Optional[str] = None
    rank: Optional[str] = None
    county: Optional[str] = None
    sub_county: Optional[str] = None


class PasswordChangeRequest(BaseSchemaCreate):
    """Schema for changing user password."""

    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)


class UserResponse(UserBase, BaseSchemaResponse):
    """Full schema for returning user details."""

    id: UUID
    is_verified: bool
    is_active: bool
    email_verified: bool
    phone_verified: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    created_by_id: Optional[UUID] = None
    updated_by_id: Optional[UUID] = None


class UserProfileResponse(BaseSchemaResponse):
    """Lightweight schema for user profile endpoint."""

    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    role: UserRole
    status: UserStatus
    profile_picture_url: Optional[HttpUrl] = None
    bio: Optional[str] = None
    county: Optional[str] = None
    sub_county: Optional[str] = None
    created_at: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: datetime
    