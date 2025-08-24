from datetime import datetime, timedelta, timezone
from uuid import UUID
from fastapi import Header, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr
from wenotify.core.config import settings
from wenotify.core.logging import logger
from wenotify.enums import UserStatus

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/users/auth/login")
GetToken = Annotated[str, Depends(oauth2_scheme)]


class UserBase(BaseModel):
    user_id: UUID
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[str] = None
    status: UserStatus
    is_verified: bool


async def get_current_user(token: GetToken):
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        user_id = payload.get("sub")
        email = payload.get("email")
        first_name = payload.get("first_name")
        last_name = payload.get("last_name")
        phone_number = payload.get("phone_number")
        role = payload.get("role")
        user_status = payload.get("status")
        is_verified = payload.get("is_verified")

        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some credentials are missing in token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            return UserBase(
                user_id=user_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                role=role,
                status=user_status,
                is_verified=is_verified
            )
        except (ValueError, TypeError) as e:
            print(f"Error creating UserBase: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Couldn't validate token data against schema",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except jwt.JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Token decode failed! {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


GetCurrentUser = Annotated[UserBase, Depends(get_current_user)]


def get_auth_header(token: GetToken, client_name: str = Header(...)) -> dict:
    return {"Authorization": f"Bearer {token}", "Client-Name": f"{client_name.upper()}"}


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict):
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
