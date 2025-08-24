import uuid
from fastapi import Header, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from typing import Annotated, Optional

from pydantic import BaseModel
from wenotify.core.config import settings
from wenotify.core.logging import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/users/auth/login")
GetToken = Annotated[str, Depends(oauth2_scheme)]

class UserBase(BaseModel):
    user_id: str
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    timezone: str = "UTC"
    role: Optional[str] = None
    permissions: dict = {}
    preferences: dict = {}

async def get_current_user(token: GetToken):
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        user_id = payload.get("sub")
        username = payload.get("username")
        email = payload.get("email")
        first_name = payload.get("first_name")
        last_name = payload.get("last_name")
        phone = payload.get("phone")
        timezone = payload.get("timezone", "UTC")
        role = payload.get("role")
        permissions = payload.get("permissions", {})
        preferences = payload.get("preferences", {})

        if not user_id or not username or not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some credentials are missing in token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            return UserBase(
                id=user_id,
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                timezone=timezone,
                role=role,
                permissions=permissions,
                preferences=preferences,
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
